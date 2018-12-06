#!/usr/bin/python
# -*- encoding: utf-8 -*-
from __future__ import print_function

import solidscraper as ss
import traceback
import argparse
import json

from time import time, sleep
from datetime import timedelta
from datetime import datetime
from dateutil import tz
try:
    from urllib.parse import quote as url_encode
except:
    from urllib import quote as url_encode

parser = argparse.ArgumentParser(
    description='LIDIC Twitter Scraper v.1.0',
    epilog=(
        "Author: Burdisso Sergio (<sergio.burdisso@gmail.com>), Phd. Student. "
        "LIDIC, Department of Computer Science, National University of San Luis "
        "(UNSL), San Luis, Argentina."
    )
)
parser.add_argument(
    'hashtags', metavar='H', type=str, nargs='*',
    help='a hashtags name (e.g. music, art, science)'
)
args = parser.parse_args()

# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
_TIMEZONE_ = tz.gettz('America/Buenos_Aires')
_UTC_TIMEZONE_ = tz.gettz('UTC')

# ss.setVerbose()
# ss.scookies.set("lang", "es")
ss.setUserAgent(ss.UserAgent.CHROME_WIN7_64)

_LIMIT_ = 100
_HASHTAGS_ = ["sports", "weather"] if not args.hashtags else args.hashtags


def fixed_print(strn, length):
    if isinstance(strn, list) or type(strn) == int:
        strn = str(strn)
    return (u"{:<%i}" % (length)).format(strn[:length])


def download_n(hashtag, N):
    """ download N tweets with hashtag <hashtag>. """

    _TAGS_QUERY_ = "%23" + url_encode(hashtag)
    has_more_items = True
    min_position = ""
    items_html = ""

    document = None
    i = 0

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

    tweet_counter = 0
    retweet_counter = 0

    _time_start_ = time()

    print("\n\nAbout to start downloading tweets by tag:")

    while has_more_items:
        try:
            print(
                "\n> downloading timeline chunk [ %s of %d tweets so far]... \n"
                %
                (
                    (tweet_counter + retweet_counter),
                    N
                )
            )
            r = ss.get(
                (
                    "https://twitter.com/i/search/timeline?f=tweets&"
                    "vertical=default&q=%s%%20lang%%3Aen&src=typd&"
                    "include_available_features=1&include_entities=1"
                    "&max_position=%s"
                )
                %
                (_TAGS_QUERY_, min_position)
            )
            if not r or not r.body:
                print("Error: no response")
                exit()  # return False

            j = json.loads(r.body)
            items_html = j["items_html"].encode("utf8")
            min_position = url_encode(j["min_position"])

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
                tweet_raw_text = node.select(".tweet-text").text().replace("\n", "")
                tweet_lang = node.select(".tweet-text").getAttribute("lang")
                tweet_lang = tweet_lang[0] if tweet_lang else ""
                tweet_timestamp = int(node.select("@data-time-ms").getAttribute("data-time")[0]) if node.select("@data-time-ms") else 0
                tweet_hashtags = [tag.text()[1:] for tag in node.select(".twitter-hashtag")]
                tweet_iscomment = node.getAttribute("data-is-reply-to") == "true"

                tweet_datetime = datetime.fromtimestamp(
                    tweet_timestamp
                ).replace(tzinfo=_UTC_TIMEZONE_).astimezone(_TIMEZONE_)

                print("|%s |%s[%s]%s\t|%s |%s |%s |%s |%s" % (
                    fixed_print(tweet_datetime.isoformat(" "), 16),
                    tweet_id,
                    tweet_lang,
                    "[r]" if tweet_retweeter else ("[c]" if tweet_iscomment else ""),
                    fixed_print(tweet_owner_id, 10),
                    fixed_print(tweet_owner_username, 16),
                    fixed_print(tweet_owner_name, 19),
                    fixed_print(tweet_mentions + tweet_hashtags, 10),
                    fixed_print(tweet_raw_text, 54) + "..."
                ))

                # paste your code here to store the tweets
                # e.g.
                # file_tweets.write("%s:%s\n" % (tweet_id, tweet_raw_text))
                # Note: file_tweets should be open having a utf-8 encoding, for instance:
                # file_tweets = io.open("tweets.txt", "w", encoding="utf-8")

                if tweet_retweeter:
                    retweet_counter += 1
                else:
                    tweet_counter += 1

            if (tweet_counter + retweet_counter) >= N:
                return False
            has_more_items = items_html

            i += 1
        except Exception as e:
            print("------------------------------------------")
            traceback.print_stack()
            print("[ error: %s ]" % str(e))
            print("[ trying again... ]")
            sleep(5)
            return False

    print(
        "\nprocess finished successfully! =D -- time:",
        timedelta(seconds=time() - _time_start_),
        " --"
    )

    return False

if __name__ == "__main__":
    ss.scookies.load()
    document = ss.load("https://twitter.com/login")

    if document.select("title").text().startswith("Login"):
        params = {
            "session[username_or_email]": "YourUser",  # <- the user (optional)
            "session[password]": "YourPassword",  # <- the password (optional)
            "authenticity_token": document.select("@name=authenticity_token").getAttribute("value")[0],
            "scribe_log": "",
            "redirect_after_login": "",
            "remember_me": "1"
        }
        ss.post("/sessions", params)
        ss.scookies.save()

    for c in _HASHTAGS_:
        print(
            "\n|||||||||||||||||||||", c.upper(), "|||||||||||||||||||||||||"
        )
        download_n(c, _LIMIT_)
    print("[ finished ]")
