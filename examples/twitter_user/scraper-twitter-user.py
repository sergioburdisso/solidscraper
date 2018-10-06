#!/usr/bin/python
from __future__ import print_function
import solidscraper as ss
import traceback
import argparse
import codecs  # utf-8 text files
import json
import os

from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from dateutil import tz
import time


def toFixed(strn, length):
    if isinstance(strn, list) or type(strn) == int:
        strn = str(strn)
    return (u"{:<%i}" % (length)).format(strn[:length])


def sumc(collection):
    total = 0
    if type(collection) == list or type(collection) == set or type(collection) == tuple:
        for e in collection:
            total += e
    else:
        for e in collection:
            total += collection[e]
    return float(total)

parser = argparse.ArgumentParser(
    description='LIDIC Twitter Scraper v.1.1',
    epilog=(
        "Author: Burdisso Sergio (<sergio.burdisso@gmail.com>), Phd. Student. "
        "LIDIC, Department of Computer Science, National University of San Luis"
        " (UNSL), San Luis, Argentina."
    )
)

parser.add_argument('USER', help="target's twitter user name")
args = parser.parse_args()


# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
_TIMEZONE_ = tz.gettz('America/Buenos_Aires')
_UTC_TIMEZONE_ = tz.gettz('UTC')

ss.setVerbose(False)
ss.scookies.set("lang", "en")
ss.setUserAgent(ss.UserAgent.CHROME_LINUX)

_XML_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<author type="twitter" url="https://twitter.com/%s" id="%s" name="%s" join_date="%s" location="%s" personal_url="%s" tweets="%s" following="%s" followers="%s" favorites="%s" age_group="xx" gender="xx" lang="xx">
    <biography>
        <![CDATA[%s]]>
    </biography>
    <documents count="%s">%s
    </documents>
</author>"""

_XML_TWEET_TEMPLATE = """
<document id="%s" timestamp="%s" lang="%s" url="https://twitter.com/%s/status/%s"><![CDATA[%s]]></document>
"""


def scrapes(user):
    _XML_TWEETS = ""
    _XML_ = ""

    _USER_ = user
    logged_in = True
    has_more_items = True
    min_position = ""
    items_html = ""

    document = None
    i = 0

    user_id = 0
    user_bio = ""
    user_url = ""
    user_name = ""
    user_favs = 0
    user_tweets = 0
    user_isFamous = False
    user_location = ""
    user_joinDate = ""
    user_following = 0
    user_followers = 0

    tweet_counter = 0
    comments_counter = 0
    mention_tweet_counter = 0
    url_tweet_counter = 0
    retweet_counter = 0

    tweet_id = 0
    tweet_lang = ""
    tweet_raw_text = ""
    tweet_datetime = None
    tweet_mentions = None
    tweet_hashtags = None
    tweet_owner_id = 0
    tweet_retweeter = False
    tweet_timestamp = 0
    tweet_owner_name = ""
    tweet_owner_username = ""

    dict_mentions_mutual = defaultdict(lambda: 0)
    dict_mentions_user = defaultdict(lambda: 0)
    dict_mentions_p = defaultdict(lambda: 0)
    dict_hashtag_p = defaultdict(lambda: 0)
    dict_retweets = defaultdict(lambda: 0)
    dict_mentions = defaultdict(lambda: 0)
    dict_hashtag = defaultdict(lambda: 0)
    dict_lang_p = defaultdict(lambda: 0)
    dict_lang = defaultdict(lambda: 0)

    _time_start_ = time.time()

    print("\nAccessing %s profile on twitter.com..." % (_USER_))
    error = True
    while error:
        try:
            user_url = "/%s/with_replies"
            res = ss.get(user_url % (_USER_), redirect=False)
            if res.status // 100 != 2:
                print("It looks like you're not logged in, I'll try to collect only what is public")
                logged_in = False
                user_url = "/%s"
            document = ss.load(user_url % (_USER_))
            if not document:
                print("nothing public to bee seen... sorry")
                return
            error = False
        except:
            time.sleep(5)

    profile = document.select(".ProfileHeaderCard")

    # user screenname
    _USER_ = profile.select(
        ".ProfileHeaderCard-screenname"
    ).then("a").getAttribute("href")

    if not _USER_:
        return

    _USER_ = _USER_[0][1:]
    _BASE_DIR_ = "_OUTPUT_/%s/" % (_USER_)
    _BASE_PHOTOS = _BASE_DIR_ + "photos/"
    _BASE_PHOTOS_PERSONAL = _BASE_PHOTOS + "personal/"
    _BASE_PHOTOS_EXTERN = _BASE_PHOTOS + "extern/"

    try:
        os.makedirs(_BASE_PHOTOS_PERSONAL)
    except:
        pass
    try:
        os.makedirs(_BASE_PHOTOS_EXTERN)
    except:
        pass

    # Is Famous
    user_isFamous = True if profile.select(".Icon--verified") else False
    # Name
    user_name = profile.select(".ProfileHeaderCard-name").then("a .ProfileHeaderCard-nameLink").text()
    # Biography
    user_bio = profile.select(".ProfileHeaderCard-bio").text()
    # Location
    user_location = profile.select(".ProfileHeaderCard-locationText").text()
    # Url
    user_url = profile.select(".ProfileHeaderCard-urlText").then("a").getAttribute("title")
    user_url = user_url[0] if user_url else ""
    # Join Date
    user_joinDate = profile.select(".ProfileHeaderCard-joinDateText").getAttribute("title")
    user_joinDate = user_joinDate[0] if user_joinDate else ""

    profileNav = document.select(".ProfileNav")
    # user id
    user_id = profileNav.getAttribute("data-user-id")[0]
    # tweets
    user_tweets = profileNav.select(".ProfileNav-item--tweets").then("a").getAttribute("title")
    user_tweets = user_tweets[0].split(" ")[0].replace(",", "") if user_tweets else 0
    # following
    user_following = profileNav.select(".ProfileNav-item--following").then("a").getAttribute("title")
    user_following = user_following[0].split(" ")[0].replace(",", "") if user_following else 0
    # followers
    user_followers = profileNav.select(".ProfileNav-item--followers").then("a").getAttribute("title")
    user_followers = user_followers[0].split(" ")[0].replace(",", "") if user_followers else 0
    # favorites
    user_favs = profileNav.select(".ProfileNav-item--favorites").then("a").getAttribute("title")
    if user_favs:
        user_favs = user_favs[0].split(" ")[0].replace(",", "")
    else:
        user_favs = ""

    user_profilePic = document.select(".ProfileAvatar").andThen("img").getAttribute("src")[0]
    print("\n> downloading profile picture...")
    ss.download(user_profilePic, _BASE_PHOTOS)

    print("\n\nAbout to start downloading user's timeline:")

    timeline_url = "https://twitter.com/i/profiles/show/%s/timeline/" % (_USER_)
    timeline_url += "%s?include_available_features=1&include_entities=1" % ("with_replies" if logged_in else "tweets")

    while has_more_items:
        try:
            print("\n> downloading timeline chunk [ %s of %s tweets so far, max_position=%s]... \n" % (tweet_counter + retweet_counter, user_tweets, min_position))
            if not min_position:
                r = ss.get(timeline_url)
                if not r:
                    break
            else:
                r = ss.get(timeline_url + "&max_position=%s" % min_position)
            if not r:
                break

            try:
                j = json.loads(r.body)
            except:
                print("[*] Error while trying to parse the JSON response, aborting...")
                has_more_items = False
                break
            items_html = j["items_html"].encode("utf8")

            document = ss.parse(items_html)
            items_html = document.select("li")
            for node in items_html:
                node = node.select("@data-tweet-id")
                if node:
                    node = node[0]
                else:
                    continue
                tweet_id = node.getAttribute("data-tweet-id")
                tweet_owner_id = node.getAttribute("data-user-id")
                tweet_owner_username = node.getAttribute("data-screen-name")
                tweet_owner_name = node.getAttribute("data-name")
                tweet_retweeter = node.getAttribute("data-retweeter")
                tweet_mentions = node.getAttribute("data-mentions")
                tweet_mentions = tweet_mentions.split() if tweet_mentions else []
                tweet_raw_text = node.select(".tweet-text").text()
                tweet_lang = node.select(".tweet-text").getAttribute("lang")
                tweet_lang = tweet_lang[0] if tweet_lang else ""
                tweet_timestamp = int(node.select("@data-time-ms").getAttribute("data-time")[0])
                tweet_hashtags = []
                tweet_iscomment = node.getAttribute("data-is-reply-to") == "true"

                for node_hashtag in node.select(".twitter-hashtag"):
                    hashtag = node_hashtag.text().upper().replace("#.\n", "")
                    tweet_hashtags.append(hashtag)

                    dict_hashtag[hashtag] += 1
                    if not tweet_retweeter:
                        dict_hashtag_p[hashtag] += 1

                tweet_links = [link for link in node.select(".tweet-text").then("a").getAttribute("href") if link.startswith("http")]

                # updating counters
                tweet_owner_username = tweet_owner_username.upper()
                for uname in tweet_mentions:

                    if uname.upper() == _USER_.upper():
                        dict_mentions_user[tweet_owner_username] += 1

                tweet_datetime = datetime.fromtimestamp(tweet_timestamp).replace(tzinfo=_UTC_TIMEZONE_).astimezone(_TIMEZONE_)

                for usermen in tweet_mentions:
                    dict_mentions[usermen.upper()] += 1
                    if not tweet_retweeter:
                        dict_mentions_p[usermen.upper()] += 1

                dict_lang[tweet_lang] += 1

                if tweet_retweeter:
                    retweet_counter += 1
                    dict_retweets[tweet_owner_username] += 1
                else:
                    if tweet_owner_id == user_id:
                        dict_lang_p[tweet_lang] += 1

                        # updating counters
                        tweet_counter += 1
                        if tweet_iscomment:
                            comments_counter += 1
                        if len(tweet_mentions):
                            mention_tweet_counter += 1
                        if len(tweet_links):
                            url_tweet_counter += 1

                        _XML_TWEETS += _XML_TWEET_TEMPLATE % (
                            tweet_id,
                            tweet_timestamp,
                            tweet_lang,
                            _USER_,
                            tweet_id,
                            tweet_raw_text
                        )

                print(
                    "|%s |%s[%s]%s\t|%s |%s |%s |%s |%s"
                    %
                    (
                        toFixed(tweet_datetime.isoformat(" "), 16),
                        tweet_id,
                        tweet_lang,
                        "r" if tweet_retweeter else ("c" if tweet_iscomment else ""),
                        toFixed(tweet_owner_id, 10),
                        toFixed(tweet_owner_username, 16),
                        toFixed(tweet_owner_name, 19),
                        toFixed(tweet_mentions + tweet_hashtags, 10),
                        toFixed(tweet_raw_text, 54) + "..."
                    )
                )

                if len(node.select("@data-image-url")):
                    img_list = node.select("@data-image-url")
                    len_imgs = len(img_list)

                    print("\n" + "- " * 61)
                    if tweet_retweeter:
                        print("\t> %i extern photo found" % (len_imgs))
                        imgs_base_path = _BASE_PHOTOS_EXTERN
                    else:
                        print("\t> %i personal photo(s) found" % (len_imgs))
                        imgs_base_path = _BASE_PHOTOS_PERSONAL

                    for elem in img_list:
                        img_url = elem.getAttribute("data-image-url")
                        print("\t\tdownloading photo from %s... \n" % (img_url))

                        ss.download(img_url, imgs_base_path)
                    print("- " * 61 + " \n")
                elif node.getAttribute("data-card2-type") == "player":
                    print("\n" + "- " * 61)
                    video = ss.load("https://twitter.com/i/cards/tfw/v1/%s?cardname=player&earned=true"%(tweet_id))
                    video_title = video.select(".TwitterCard-title").text()
                    video_url = video.select("iframe").getAttribute("src")[0]
                    print("\t> new video '%s' found [ %s ]" % (video_title, video_url))
                    print("\n" + "- " * 61)
                min_position = tweet_id

            has_more_items = j["has_more_items"] and items_html
            i += 1
        except Exception as e:
            print("------------------------------------------")
            traceback.print_stack()
            print("[ error: %s ]" % str(e))
            print("[ trying again... ]")
            time.sleep(5)

    print("\nprocess finished successfully! =D -- time:", timedelta(seconds=time.time() - _time_start_) , " --")

    _XML_ = _XML_TEMPLATE % (
        _USER_,
        user_id,
        user_name,
        user_joinDate,
        user_location,
        user_url,
        user_tweets,
        user_following,
        user_followers,
        user_favs,
        user_bio.replace("\r\n", ""),
        tweet_counter,
        _XML_TWEETS
    )

    fxml = codecs.open("%s%s.xml" % (_BASE_DIR_, _USER_), "w", "utf-8")
    fxml.write(_XML_)
    fxml.close()

    personal_lang = ""
    for t in sorted(dict_lang_p.items(), key=lambda k: -k[1])[:2]:
        personal_lang += "\t%s: %.2f%% (%s)" % (t[0], t[1] / sumc(dict_lang_p) * 100 , t[1])

    lang = ""
    for t in sorted(dict_lang.items(), key=lambda k: -k[1])[:2]:
        lang += "\t%s: %.2f%% (%s)" % (t[0], t[1] / sumc(dict_lang) * 100, t[1])

    mentions_user = ""
    for t in sorted(dict_mentions_user.items(), key=lambda k: -k[1]):
        mentions_user += "\t%s(%s)" % t

    personal_hashtags = ""
    for t in sorted(dict_hashtag_p.items(), key=lambda k: -k[1]):
        personal_hashtags += "\t%s: %s\n" % t

    hashtags = ""
    for t in sorted(dict_hashtag.items(), key=lambda k: -k[1]):
        hashtags += "\t%s: %s\n" % t

    personal_mentions = ""
    for t in sorted(dict_mentions_p.items(), key=lambda k: -k[1]):
        personal_mentions += "\t%s: %s\n" % t
        if t[0] in dict_mentions_user:
            dict_mentions_mutual[t[0]] += 1

    mentions_mutual = ""
    for t in sorted(dict_mentions_mutual.items(), key=lambda k: -k[1]):
        mentions_mutual += "\t%s(%s)" % t

    mentions = ""
    for t in sorted(dict_mentions.items(), key=lambda k: -k[1]):
        mentions += "\t%s: %s\n" % t

    retweets = ""
    for t in sorted(dict_retweets.items(), key=lambda k: -k[1]):
        retweets += "\t%s: %s\n" % t

    output = """
    \n\n
    Overview:
    ---------

    Id: %s
    Name: %s
    Join Date: %s
    Biography: %s
    Location: %s
    Url: %s
    Is Famous: %s
    Tweets: %s
    Following: %s
    Followers: %s
    Favorites: %s


    Number of tweets captured: %s (%s tweets / %s retweets)
    --------------------------

    > Personal language:
    %s

    > Total language:
    %s

    > People who has mentioned him:
    %s

    > Mutual Mentions:
    %s

    > Personal Hashtags:
    %s

    > Total Hashtags:
    %s

    > Personal Mentions:
    %s

    > Total Mentions:
    %s

    > Retweets:
    %s

    """
    try:
        output = output % (
            user_id,
            user_name,
            user_joinDate,
            user_bio.replace("\r\n", ""),
            user_location,
            user_url,
            user_isFamous,
            user_tweets,
            user_following,
            user_followers,
            user_favs,
            tweet_counter + retweet_counter, tweet_counter, retweet_counter,
            personal_lang,
            lang,
            mentions_user,
            mentions_mutual,
            personal_hashtags,
            hashtags,
            personal_mentions,
            mentions,
            retweets
        )
    except:
        pass

    print(output)

    print("[ tweets saved in %s%s.xml ]" % (_BASE_DIR_, _USER_))
    print("[ profile picture saved in %s ]" % _BASE_PHOTOS)
    print("[ images uploaded by the user saved in %s ]" % _BASE_PHOTOS_PERSONAL)
    print("[ images retweeted by the user saved in %s ]" % _BASE_PHOTOS_EXTERN)
    print("[ finised ]\n")


ss.scookies.load()
document = ss.load("https://twitter.com/login")
if document.select("title").text().startswith("Login"):
    params = {
        "session[username_or_email]": "",  # <- your user
        "session[password]": "",  # <- your password
        "authenticity_token": document.select("@name=authenticity_token").getAttribute("value")[0],
        "scribe_log": "",
        "redirect_after_login": "",
        "remember_me": "1"
    }
    ss.post("/sessions", params)
    ss.scookies.save()

if __name__ == "__main__":
    scrapes(args.USER)
