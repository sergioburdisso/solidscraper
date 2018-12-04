# -*- coding: utf-8 -*-

import re
try:  # python 3
    import http.client as httplib
    from urllib.parse import urlencode
except:  # python 2
    import httplib
    from urllib import urlencode


__ERRORS__ = {
    "send": "error: couldn't send the request to the server",
    "url_format": "error: the %s url is not valid"
}
__RE_URL__ = (
    r"(?P<protocol>https?://)?"
    "(?:(?P<base_address>[^/:]+)(?::(?P<port>\d+))?)?"
    "(?P<path>/.*)?"
)
__TIMEOUT__ = 60


class SolidHTTPException(Exception):
    pass


class method:
    POST = "POST"
    GET = "GET"


class URL:
    def __init__(self, prot, dom, port, path):
        self.protocol = prot
        self.domain = dom
        self.port = port
        self.path = path

    def getBaseUrl(s):
        return s.protocol + s.domain + (
            ("[%s]" % s.port) if s.port and s.port != "80" else ""
        )

    def getUrl(s):
        return s.getBaseUrl() + s.path

    def __str__(self):
        return self.getUrl()

__last_url__ = URL("http://", "", "", "")


class Response:
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body

    def getHeader(self, name):
        for h in self.headers:
            if h[0].lower() == name.lower():
                return h[1]
        return ""


def __request__(method, url, body, headers):
    global __last_url__

    __last_url__ = parseUrl(url)

    if not url:
        return False

    _prot = __last_url__.protocol
    _addr = __last_url__.domain
    _port = __last_url__.port
    _path = __last_url__.path

    if _prot.startswith("https"):
        _conn = httplib.HTTPSConnection(_addr, _port, timeout=__TIMEOUT__)
    else:
        _conn = httplib.HTTPConnection(_addr, _port, timeout=__TIMEOUT__)

    try:
        _conn.request(method, _path, body, headers)
    except Exception as e:
        if str(e).find("timed out") != -1:
            raise httplib.ResponseNotReady
        else:
            raise SolidHTTPException("%s (%s)" % (__ERRORS__["send"], str(e)))

    res = _conn.getresponse()
    headers = res.getheaders()
    return Response(res.status, headers, res.read())


def parseUrl(url):
    m = re.match(__RE_URL__, url.strip())
    if not m:
        raise SolidHTTPException(__ERRORS__["url_format"] % url)

    _prot = m.group("protocol") or __last_url__.protocol
    _addr = m.group("base_address") or __last_url__.domain
    _port = m.group("port")
    _path = m.group("path") or "/"
    _prot = _prot.lower()

    return URL(_prot, _addr, _port, _path)


def get(url, headers={}):
    return __request__(method.GET, url, None, headers)


def post(url, data, headers={}):
    try:  # python 2
        if type(data) != str and type(data) != unicode:
            data = urlencode(data)
    except:  # python 3
        if type(data) != str:
            data = urlencode(data)
    return __request__(method.POST, url, data, headers)


def getLastUrl():
    return __last_url__.getUrl()
