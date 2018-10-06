
# Solid Scraper

Easy to use JQuery-Like API for Web Scraping/Crawling. It also supports Cookies and custom User Agents. Solidscraper is compatible with **Python 2 and 3**.

---
## 1. Installation

````
pip install solidscraper
````

**Note:** if you already have installed it, and wanted the latest version, then use the following command to update `solidscraper`:

````
pip install --upgrade solidscraper
````

---
## 2. "Hello World" Examples

Getting all url of all links:

````python
import solidscraper as ss

doc = ss.load("https://www.example.com/the/path")

# print the list of urls from all <a> elements
print(doc.select("a").getAttribute("href"))
````

Getting all url of all links inside \<div\>s whose class id is 'links':

````python
import solidscraper as ss

doc = ss.load("https://www.example.com/the/path")

# print the list of urls from all <a> elements inside <div id="links">
print(doc.select("div #links").then("a").getAttribute("href"))
````

Getting the text of all \<span\> elements inside \<p\> whose class are 'info':

````python
import solidscraper as ss

doc = ss.load("https://www.example.com/the/path")

# print the text of all <span> elements inside <p class="info">
print(doc.select("p .info").then("span").text())
````

**Note:** these examples use the python 3 print function, in case you want to run them with python 2, either replace the `print()` function with the python 2 `print` statement or add the following import line as the first statement of your code: `from __future__ import print_function`.

---
## 3. "Real World" Examples

The `examples` [folder above](https://github.com/sergioburdisso/solidscraper/tree/master/examples/) contains two fully functional examples: one to download tweets by hashtags and another to download complete users timeline (tweets and images). Both scripts were completely built using `solidscraper`.