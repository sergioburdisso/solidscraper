# -*- coding: utf-8 -*-

from __future__ import print_function
from bs4 import BeautifulSoup
from bs4 import element
import re

__CHARSET__ = "utf-8"


class SolidDomException(Exception):
    pass


class SolidNodeList(list):
    def __init__(self, *args):
        list.__init__(self, *args)

    def __applytoall__(self, funtion, *args):
        _output = SolidNodeList()

        for item in self:
            o = funtion(item, *args)

            if isinstance(o, list):
                _output.extend(o)
            else:
                _output.append(o)

        return _output

    def getAttribute(self, *args):
        _result = []
        for e in self:
            _result.append(e.getAttribute(*args))
        return _result

    def text(self):
        _text = u""
        for e in self:
            _text += e.text() + " "
        return _text

    def textBytes(self):
        _text = u"".encode(__CHARSET__)
        for e in self:
            _text += e.textBytes() + " "
        return _text

    def html(self):
        _html = u""
        for e in self:
            _html += e.html() + u"\n"
        return _html

    def htmlBytes(self):
        _html = u"".encode(__CHARSET__)
        _NL = u"\n".encode(__CHARSET__)
        for e in self:
            _html += e.htmlBytes() + _NL
        return _html

    def select(self, criteria, recursive=True):
        return self.__applytoall__(SolidNode.select, criteria, recursive)

    def s(self, criteria, recursive=True):
        return self.select(criteria, recursive)

    def then(self, criteria, recursive=True):
        return self.select(criteria, recursive)

    def andThen(self, criteria, recursive=True):
        return self.select(criteria, recursive)

    def andFinally(self, criteria, recursive=True):
        return self.select(criteria, recursive)

    def has(self, element):
        for e in self:
            if e.__node__ is element.__node__:
                return True
        return False

    def intersect(self, set):
        _result = SolidNodeList()
        for e in self:
            if set.has(e):
                _result.append(e)
        return _result

    def append(self, item):
        if not isinstance(item, SolidNode):
            item = SolidNode(item)
        list.append(self, item)

    def extend(self, items):
        list.extend(
            self,
            SolidNodeList(items).__applytoall__(
                lambda e: SolidNode(e) if not isinstance(e, SolidNode) else e
            )
        )


class SolidNode:
    def __init__(self, node):
        self.__node__ = node

    def __select__(self, criteria, recursive):
        output = SolidNodeList()
        value = criteria[1:]
        child_nodes = [
            c for c in self.__node__.children
            if type(c) == element.Tag
        ]

        if criteria.startswith("."):
            if self.__node__.attrs.__contains__("class"):
                atrr_value = " ".join(self.__node__["class"])
                if re.search(
                    "(?:^|\\s)%s(?:$|\\s)" % (value), atrr_value, re.I
                ):
                    output.append(self.__node__)
            for child in child_nodes:
                if recursive:
                    output.extend(SolidNode(child).select(criteria, True))
        elif criteria.startswith("#"):
            if self.__node__.attrs.__contains__("id"):
                atrr_value = self.__node__["id"]
                if atrr_value == value:
                    output.append(self.__node__)
            for child in child_nodes:
                if recursive:
                    output.extend(SolidNode(child).select(criteria, True))
        elif criteria.startswith("@"):
            value = value.split("=")

            if self.__node__.attrs.__contains__(value[0]) and (
                len(value) == 1 or self.__node__[value[0]] == value[1]
            ):
                output.append(self.__node__)

            for child in child_nodes:
                if recursive:
                    output.extend(SolidNode(child).select(criteria, True))
        else:
            try:
                output.extend(self.__node__.find_all(criteria))
            except:
                pass

        return output

    def __text__(self):
        return self.__node__.get_text(".\n", strip=True)

    def getAttribute(self, name):
        if self.__node__.attrs.__contains__(name) and self.__node__.name:
            return self.__node__[name]
        else:
            return ""

    def getChildNodes(self):
        return self.__node__.children

    def html(self):
        return self.__node__.prettify()

    def htmlBytes(self):
        return self.__node__.prettify().encode(__CHARSET__)

    def text(self):
        return re.sub(r"(\s|\n)+", r"\g<1>", self.__text__())

    def textBytes(self):
        return self.text().encode(__CHARSET__)

    def select(self, criteria, recursive=True):
        criteria = re.split(r"\s+", criteria.strip())
        if not len(criteria):
            return SolidNodeList()

        _result = self.__select__(criteria[0], recursive)

        for i in range(1, len(criteria)):
            _result = _result.intersect(self.__select__(criteria[i], recursive))

        return _result

    def selectUnion(self, criteria, recursive=True):
        criteria = re.split(r"\s+", criteria.strip())
        if not len(criteria):
            return SolidNodeList()

        _result = self.__select__(criteria[0], recursive)

        for i in range(1, len(criteria)):
            _result.extend(self.__select__(criteria[i], recursive))

        return _result

    def s(self, criteria, recursive=True):
        return self.select(criteria, recursive)

    def then(self, criteria, recursive=True):
        return self.select(criteria, recursive)

    def andThen(self, criteria, recursive=True):
        return self.select(criteria, recursive)

    def andFinally(self, criteria, recursive=True):
        return self.select(criteria, recursive)


def create(html, charset="utf-8"):
    global __CHARSET__
    __CHARSET__ = charset

    _snode = None

    try:
        _snode = SolidNode(BeautifulSoup(html, "html.parser"))
    except Exception as e:
        raise SolidDomException(
            "Error while trying to parse the HTML response: %s" % str(e)
        )

    return _snode
