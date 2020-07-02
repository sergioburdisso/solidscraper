#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

from . import solidcookies as scookies
from . import solidhttp as shttp
from . import soliddom as sdom
import re
import os

__version__ = '0.7.7'
__license__ = 'MIT'


class UserAgent:
    CHROME_WIN7_64 = (
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"
    )
    CHROME_MAC = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"
    )
    CHROME_LINUX = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"
    )

    FIREFOX_WIN7_64 = (
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) "
        "Gecko/20100101 Firefox/38.0"
    )
    FIREFOX_MAC = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) "
        "Gecko/20100101 Firefox/38.0"
    )
    FIREFOX_LINUX = (
        "Mozilla/5.0 (X11; Linux x86_64; rv:38.0) "
        "Gecko/20100101 Firefox/38.0"
    )

    SAFARI_MAC = (
        "Mozilla/5.0"" (Macintosh; Intel Mac OS X 10_10_3) "
        "AppleWebKit/600.6.3 (KHTML, like Gecko) Version/8.0.6 Safari/600.6.3"
    )

    IE9_WIN7_64 = (
        "Mozilla/5.0 "
        "(compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)"
    )
    IE8_WINXP = (
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; "
        "SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 1.1.4322)"
    )

    MOBILE_SAMSUNG_NOTE_II = (
        "Mozilla/5.0 (Linux; U; Android 4.1; en-us; GT-N7100 Build/JRO03C) Ap"
        "pleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
    )
    MOBILE_IPHONE6 = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600"
        ".1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4"
    )
    MOBILE_SAFARI = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600"
        ".1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4"
    )
    MOBILE_BLACKBERRY_Z30 = (
        "Mozilla/5.0 (BB10; Touch) AppleWebKit/537.10+ (KHTML, like Gecko) "
        "Version/10.0.9.2372 Mobile Safari/537.10+"
    )

    _DEFAULT = CHROME_WIN7_64

__RE_COOKIE__ = r"(?P<key>[\w_-]+?)\s*=\s*(?P<value>[^\s;]+)"
__ERRORS__ = {}

__http_headers__ = {
    "User-Agent": UserAgent.IE9_WIN7_64,
    "Cookie": "",
    "Referer": ""
}
__op_verbose__ = False
__op_cookies__ = True


def __request__(method, url, params, redirect=True):
    global __http_headers__, __op_cookies__

    _p_url = shttp.parseUrl(url)

    __http_headers__["Cookie"] = scookies.get(_p_url.domain, _p_url.path)
    __http_headers__["Referer"] = shttp.getLastUrl()

    if method == shttp.method.POST:
        if __op_verbose__:
            print("[ sscraper: sending POST to ", url, "]")
        __http_post_headers__ = __http_headers__.copy()
        __http_post_headers__["Content-Type"] = (
            "application/x-www-form-urlencoded"
        )
        _response = shttp.post(url, params, __http_post_headers__)
    else:
        if __op_verbose__:
            print("[ sscraper: sending GET to ", url, "]")
        _response = shttp.get(url, __http_headers__)

    if not _response:
        return False

    if __op_cookies__:
        scookies.setFromHeader(_response.getHeader("Set-Cookie"))

    if redirect:
        _r_url = ""
        if _response.status // 100 == 3:

            _r_url = _response.getHeader("location")
            if __op_verbose__:
                print("[ sscraper: redirecting to ", _r_url, "]")

        elif len(_response.body) < 512 and b'location.replace("http' in _response.body:

            _r_url = re.search('(https?://.*?)[ ">]', _response.body).group(1)
            if __op_verbose__:
                print("[ sscraper: redirecting by JavaScript to ", _r_url, "]")

        if _r_url:
            if _r_url == url:
                if __op_verbose__:
                    print("[ sscraper: redirection to ", _r_url, " aborted]")
                return _response
            return get(_r_url)

    return _response


def setUserAgent(value):
    __http_headers__["User-Agent"] = value


def enableAutoCookies():
    global __op_cookies__
    __op_cookies__ = True


def disableAutoCookies():
    global __op_cookies__
    __op_cookies__ = False


def clearCookies():
    scookies.clear()


def setVerbose(value=True):
    global __op_verbose__
    __op_verbose__ = value


def lastVisitedUrl():
    return shttp.getLastUrl()


def get(url, redirect=True):
    return __request__(shttp.method.GET, url, "", redirect)


def post(url, params, redirect=True):
    return __request__(shttp.method.POST, url, params, redirect)


def parse(html, charset="utf-8"):
    if __op_verbose__:
        print("[ sscraper: parsing HTML... ]")
    return sdom.create(html, charset)


def load(url):
    _charset = "utf-8"

    _res = get(url)

    if _res.getHeader("Content-Type").find("ht") != -1:
        try:
            # try to get charset from the Content-Type HTTP header
            _charset = re.search(
                r"charset\s*=([^\s]+)",
                _res.getHeader("Content-Type")
            ).group(1)
        except:
            try:
                # otherwise try to get it from the HTML <meta charset>
                _charset = re.search(
                    r" charset\s*=[\"']?([^\s\"']+)[\"']?",
                    _res.body
                ).group(1)
            except:
                pass
    else:
        _res.body = (
            "<html><head><meta><title></title></head>"
            "<body></body></html>"
        )

    return parse(_res.body, _charset)


def save(res, filename="response", path=""):
    data = res.body
    (filename, ext) = os.path.splitext(filename)
    try:
        os.makedirs(path)
    except OSError:
        pass

    f = open(os.path.join(path, filename + ext), "w" if type(data) != bytes else "wb")
    f.write(data)
    f.close()

    return ext


def download(url, path="", use_original_path=False):
    """
    Downloads the file specified by the url and stores it in the given path
    """
    if __op_verbose__:
        print("[ sscraper: downloading ", url, "]")
    (dirname, filename) = os.path.split(url)
    if filename == '':
        filename = "index"

    if not use_original_path:
        return save(get(url), filename, path)
    else:
        path = os.path.join(
            path,
            os.path.dirname(shttp.parseUrl(url).path)[1:]
        )
        return save(get(url), filename, path)
