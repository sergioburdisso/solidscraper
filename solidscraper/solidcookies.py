# -*- coding: utf-8 -*-

import json
import re


# see https://tools.ietf.org/html/rfc6265#section-4.1 for formal specification
class SolidCookiesParser:
    class _TOKEN:
        SETC = 0x00
        SP = 0x01
        SCOLON = 0x02
        EQ = 0x03
        TOKEN = 0x04
        DQUOTE = 0x05
        COCTET = 0x06
        EXPIRESAV = 0x07
        COMMA = 0x08
        GMTUTC = 0x09
        DIGIT4 = 0x0A
        DIGIT2 = 0x0B
        DIGIT = 0x0C
        DATEHYPSP = 0x0D
        COLON = 0x0E
        WKDAY = 0x0F
        WEEKDAY = 0x10
        MONTH = 0x11
        MAXAGEAV = 0x12
        MAXAGEVAL = 0x13
        DOMAINAV = 0x14
        SUBDOMAIN = 0x15
        PATHAV = 0x16
        PATHVALUE = 0x17
        SECUREAV = 0x18
        HTTPONLYAV = 0x19
        EXTENSNAV = 0x1A

    __cursor__ = 0
    __input__ = ""
    __output__ = []
    __cookie__ = None

    def __lookup__(s, token):
        return s.__match__(token, False)

    def __match__(s, token, consume=True):
        _re_strn = ""

        if token == s._TOKEN.SETC:
            _re_strn = r'Set-Cookie:'
        elif token == s._TOKEN.SP:
            _re_strn = r'\s+'
        elif token == s._TOKEN.SCOLON:
            _re_strn = r';'
        elif token == s._TOKEN.EQ:
            _re_strn = r'='
        elif token == s._TOKEN.TOKEN:
            _re_strn = r'[^\\()\]\[<>"@,;:/?={}\s]+'
        elif token == s._TOKEN.DQUOTE:
            _re_strn = r'"'
        elif token == s._TOKEN.COCTET:
            _re_strn = r'[^\s",\\;]*'
        elif token == s._TOKEN.EXPIRESAV:
            _re_strn = r'Expires='
        elif token == s._TOKEN.COMMA:
            _re_strn = r','
        elif token == s._TOKEN.GMTUTC:
            _re_strn = r'GMT|UTC'
        elif token == s._TOKEN.DIGIT4:
            _re_strn = r'\d{4}'
        elif token == s._TOKEN.DIGIT2:
            _re_strn = r'\d{2}'
        elif token == s._TOKEN.DIGIT:
            _re_strn = r'\d'
        elif token == s._TOKEN.DATEHYPSP:
            _re_strn = r'[-\s]'
        elif token == s._TOKEN.COLON:
            _re_strn = r':'
        elif token == s._TOKEN.WKDAY:
            _re_strn = r'Mon|Tue|Wed|Thu|Fri|Sat|Sun'
        elif token == s._TOKEN.WEEKDAY:
            _re_strn = r'Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday'
        elif token == s._TOKEN.MONTH:
            _re_strn = r'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'
        elif token == s._TOKEN.MAXAGEAV:
            _re_strn = r'Max-Age='
        elif token == s._TOKEN.MAXAGEVAL:
            _re_strn = r'[1-9]\d*'
        elif token == s._TOKEN.DOMAINAV:
            _re_strn = r'Domain='
        elif token == s._TOKEN.SUBDOMAIN:
            _re_strn = r'([a-zA-Z](?:[\w-]*\w)?|\.[a-zA-Z](?:[\w-]*\w)?)+'
        elif token == s._TOKEN.PATHAV:
            _re_strn = r'Path='
        elif token == s._TOKEN.PATHVALUE:
            _re_strn = r'[^;,]*'
        elif token == s._TOKEN.SECUREAV:
            _re_strn = r'Secure'
        elif token == s._TOKEN.HTTPONLYAV:
            _re_strn = r'HttpOnly'
        elif token == s._TOKEN.EXTENSNAV:
            _re_strn = r'[^;,]*'

        m = re.match(_re_strn, s.__input__[s.__cursor__:], re.I)

        if m:
            if consume:
                s.__cursor__ += m.end(0)
            return m.group(0)
        return None

    # set-cookie-header = "Set-Cookie:" SP set-cookie-string
    def __set_cookie_header__(s):
        s.__cookie__ = {
            "name": None, "value": None,
            "domain": None, "path": None
        }
        s.__set_cookie_string__()
        s.__output__.append(s.__cookie__)

    # set-cookie-string = cookie-pair *( ";" SP cookie-av )
    def __set_cookie_string__(s):
        s.__cookie_pair__()

        while s.__lookup__(s._TOKEN.SCOLON):
            s.__match__(s._TOKEN.SCOLON)
            s.__match__(s._TOKEN.SP)
            s.__cookie_av__()

    # cookie-pair = cookie-name "=" cookie-value
    def __cookie_pair__(s):
        s.__cookie__["name"] = s.__cookie__name__()
        s.__match__(s._TOKEN.EQ)
        s.__cookie__["value"] = s.__cookie__value__()

    # cookie-name = token;  token defined in
    # http://tools.ietf.org/html/rfc2616#section-2.2
    def __cookie__name__(s):
        return s.__match__(s._TOKEN.TOKEN)

    # cookie-value = *cookie-octet / ( DQUOTE *cookie-octet DQUOTE )
    def __cookie__value__(s):

        if s.__lookup__(s._TOKEN.DQUOTE):
            _value = s.__match__(s._TOKEN.DQUOTE)
            _value += s.__match__(s._TOKEN.COCTET)
            _value += s.__match__(s._TOKEN.DQUOTE) or "\""
        else:
            _value = s.__match__(s._TOKEN.COCTET)

        return _value

    # cookie-av = expires-av / max-age-av / domain-av /
    #             path-av / secure-av / httponly-av /
    #             extension-av
    def __cookie_av__(s):
        if s.__lookup__(s._TOKEN.EXPIRESAV):
            # "Expires=" sane-cookie-date
            s.__match__(s._TOKEN.EXPIRESAV)
            s.__sane_cookie_date__()

        elif s.__lookup__(s._TOKEN.MAXAGEAV):
            # max-age-av = "Max-Age=" non-zero-digit *DIGIT
            s.__match__(s._TOKEN.MAXAGEAV)
            s.__match__(s._TOKEN.MAXAGEVAL)

        elif s.__lookup__(s._TOKEN.DOMAINAV):
            # domain-av = "Domain=" domain-value
            s.__match__(s._TOKEN.DOMAINAV)
            s.__cookie__["domain"] = s.__domain_value__()

        elif s.__lookup__(s._TOKEN.PATHAV):
            # path-av = "Path=" path-value
            s.__match__(s._TOKEN.PATHAV)
            s.__cookie__["path"] = s.__path_value__()

        elif s.__lookup__(s._TOKEN.SECUREAV):
            # secure-av = "Secure"
            s.__match__(s._TOKEN.SECUREAV)

        elif s.__lookup__(s._TOKEN.HTTPONLYAV):
            # httponly-av = "HttpOnly"
            s.__match__(s._TOKEN.HTTPONLYAV)

        else:
            #  extension-av = *<any CHAR except CTLs or ";">
            s.__match__(s._TOKEN.EXTENSNAV)

    # domain-value = <subdomain> ;
    # defined in [RFC1034], Section 3.5
    # (https://tools.ietf.org/html/rfc1034#section-3.5)
    def __domain_value__(s):
        return s.__match__(s._TOKEN.SUBDOMAIN)

    # path-value = *<any CHAR except CTLs or ";">
    def __path_value__(s):
        return s.__match__(s._TOKEN.PATHVALUE)

    # https://tools.ietf.org/html/rfc2616#section-3.3.1
    # HTTP-date = rfc1123-date | rfc850-date | asctime-date
    def __sane_cookie_date__(s):
        if s.__lookup__(s._TOKEN.WEEKDAY):
            s.__rfc850_date__()
        else:
            s.__match__(s._TOKEN.WKDAY)
            if s.__lookup__(s._TOKEN.COMMA):
                s.__rfc1123_date__()
            else:
                s.__asctime_date__()

    # rfc1123-date = wkday "," SP date1 SP time SP "GMT"
    def __rfc1123_date__(s):
        s.__match__(s._TOKEN.COMMA)
        s.__match__(s._TOKEN.SP)
        s.__date1__()
        s.__match__(s._TOKEN.SP)
        s.__time__()
        s.__match__(s._TOKEN.SP)
        s.__match__(s._TOKEN.GMTUTC)

    # rfc850-date  = weekday "," SP date1 SP time SP "GMT"
    def __rfc850_date__(s):
        s.__match__(s._TOKEN.WEEKDAY)
        s.__match__(s._TOKEN.COMMA)
        s.__match__(s._TOKEN.SP)
        s.__date1__()
        s.__match__(s._TOKEN.SP)
        s.__time__()
        s.__match__(s._TOKEN.SP)
        s.__match__(s._TOKEN.GMTUTC)

    # asctime-date = wkday SP date2 SP time SP 4DIGIT
    def __asctime_date__(s):
        s.__match__(s._TOKEN.SP)
        s.__date2__()
        s.__match__(s._TOKEN.SP)
        s.__time__()
        s.__match__(s._TOKEN.SP)
        s.__match__(s._TOKEN.DIGIT4)

    # date1 = 2DIGIT SP month SP 4DIGIT
    def __date1__(s):
        s.__match__(s._TOKEN.DIGIT2)
        s.__match__(s._TOKEN.DATEHYPSP)
        s.__match__(s._TOKEN.MONTH)
        s.__match__(s._TOKEN.DATEHYPSP)
        s.__match__(s._TOKEN.DIGIT4)

    # date2 = month SP ( 2DIGIT | ( SP 1DIGIT ))
    def __date2__(s):
        s.__match__(s._TOKEN.MONTH)
        s.__match__(s._TOKEN.SP)

        if s.__lookup__(s._TOKEN.SP):
            s.__match__(s._TOKEN.SP)
            s.__match__(s._TOKEN.DIGIT)
        else:
            s.__match__(s._TOKEN.DIGIT2)

    # time = 2DIGIT ":" 2DIGIT ":" 2DIGIT
    def __time__(s):
        s.__match__(s._TOKEN.DIGIT2)
        s.__match__(s._TOKEN.COLON)
        s.__match__(s._TOKEN.DIGIT2)
        s.__match__(s._TOKEN.COLON)
        s.__match__(s._TOKEN.DIGIT2)

    # cookies = set-cookie-header *("," set-cookie-header)
    def parse(s, strn):
        s.__cursor__ = 0
        s.__input__ = strn
        s.__output__ = []
        s.__cookie__ = None

        if s.__lookup__(s._TOKEN.SETC):
            s.__match__(s._TOKEN.SETC)
            s.__match__(s._TOKEN.SP)

        s.__set_cookie_header__()
        while s.__lookup__(s._TOKEN.COMMA):
            s.__match__(s._TOKEN.COMMA)
            s.__match__(s._TOKEN.SP)
            s.__set_cookie_header__()

        return s.__output__

__COOKIES_FILE__ = "sscraper.scookies.dat"
__cookies__ = {"*": {}}
__cookies_parser__ = SolidCookiesParser()
__last_domain__ = "*"


def get(domain, path):
    global __last_domain__

    __last_domain__ = domain or __last_domain__
    _cookies = ""
    domain = "." + domain

    for p in __cookies__["*"]:
        if path.startswith(p):
            for cookie in __cookies__["*"][p]:
                _cookies += "%s=%s; " % (cookie, __cookies__["*"][p][cookie])

    for dom in __cookies__:
        if domain.endswith(dom):
            for p in __cookies__[dom]:
                if path.startswith(p):
                    for cookie in __cookies__[dom][p]:
                        _cookies += "%s=%s; " % (
                            cookie, __cookies__[dom][p][cookie]
                        )
    return _cookies


def setFromHeader(cookieHeader):
    _newCookies = __cookies_parser__.parse(cookieHeader)
    for _cookie in _newCookies:
        set(
            _cookie["name"], _cookie["value"],
            _cookie["domain"], _cookie["path"]
        )


def set(name, value, domain="*", path="/"):
    path = path or "/"
    # "If the server omits the Domain attribute, the user agent will return the
    # cookie only to the origin server"
    # (RFC6265 section 4.1.2.3.-The Domain Attribute )
    domain = domain or __last_domain__
    if domain not in __cookies__:
        __cookies__[domain] = {}

    if path not in __cookies__[domain]:
        __cookies__[domain][path] = {}

    __cookies__[domain][path][name] = value


def load():
    global __cookies__
    try:
        _c = open(__COOKIES_FILE__, "r")
        __cookies__ = dict(json.load(_c))
        _c.close()
    except:
        pass


def save():
    global __cookies__
    _c = open(__COOKIES_FILE__, "w")
    json.dump(__cookies__, _c)
    _c.close()


def clear():
    global __cookies__, __last_domain__
    _c = open(__COOKIES_FILE__, "w")
    _c.write("")
    _c.close()

    __cookies__ = {"*": {}}
    __last_domain__ = "*"
