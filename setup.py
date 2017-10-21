#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from os import path
from io import open
from setuptools import setup

name = 'solidscraper'
description = "This package lets your script scrape web sites. JQuery-Like API."


def read_requirements(file_name):
    """Read the requirements from the file."""
    requirements = []
    with open(path.join(CWD, file_name), encoding='utf8') as reqs:
        for line in reqs:
            _r = re.match(r"\s*-r\s+([^\s]+)", line)
            _comment = re.match(r"\s*#.*", line)

            # if it indicates we must import (-r)equests from another file...
            if _r:
                requirements += read_requirements(_r.group(1))
            elif not _comment:
                requirements.append(line.strip())
    return requirements

CWD = path.abspath(path.dirname(__file__))
with open(path.join(CWD, '%s/__init__.py' % name), encoding='utf8') as init_py:
    init_src = init_py.read()

    RE = r"%s\s*=\s*['\"]([^'\"]+)['\"]"

    package = {
        '__version__': re.search(RE % '__version__', init_src).group(1),
        '__license__': re.search(RE % '__license__', init_src).group(1)
    }

with open(path.join(CWD, 'README.rst'), encoding='utf8') as README:
    long_description = README.read()

setup(
    name=name,
    version=package['__version__'],
    description=description,
    author='Sergio Burdisso',
    author_email='sergio.burdisso@gmail.com',
    url='https://github.com/sergioburdisso/%s' % name,
    packages=[name],
    long_description=long_description,
    license=package['__license__'],
    download_url='https://github.com/sergioburdisso/%s/tarball/v%s'
                 % (name, package['__version__']),
    keywords=[
        'scrape', 'crawler',
        'crawl', 'scraper'
    ],
    classifiers=[
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Programming Language :: Python',
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    zip_safe=False,
    include_package_data=True,
    install_requires=read_requirements("requirements.txt")
)
