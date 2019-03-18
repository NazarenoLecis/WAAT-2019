import urllib2
from urlparse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup


class Page(object):

    def __init__(self, address, links, text=''):
        self.address, self.links, self.text = address, links, text


class Crawler(object):

    def __init__(self, startUrl, maxDepth=2):
        self.startUrl, self.maxDepth = startUrl, maxDepth
        self.web = []

    def crawlePages(self, url, depth=0):
        print depth, url.geturl()
        if depth >= self.maxDepth:
            return self.web
        try:
            page = requests.get(url.geturl()).text
        except Exception:
            return self.web
        soup = BeautifulSoup(page, "html.parser")
        links = []
        for anchor in soup.findAll('a', href=True):
            link = urlparse(anchor['href'])
            if not link.netloc:
                link = urlparse(urljoin(url.geturl(), link.path))
            links += [link.geturl()]
        visited = set([page.address for page in self.web])
        links = list(set(links))
        links = filter(lambda l: l not in visited, links)
        self.web += [Page(url.geturl(), links, soup.text)]
        for link in links:
            self.crawlePages(urlparse(link), depth + 1)
        return self.web


def crawler(url, depth=0, maxDepth=2, web=[]):
    print depth, url.geturl()
    if depth >= maxDepth:
        return web
    try:
        page = requests.get(url.geturl()).text
    except Exception:
        return web
    soup = BeautifulSoup(page, "html.parser")
    links = []
    for anchor in soup.findAll('a', href=True):
        link = urlparse(anchor['href'])
        if not link.netloc:
            link = urlparse(urljoin(url.geturl(), link.path))
        links += [link.geturl()]
    visited = set([page.address for page in web])
    links = list(set(links))
    links = filter(lambda l: l not in visited, links)
    web += [Page(url.geturl(), links, soup.text)]
    for link in links:
        crawler(urlparse(link), depth + 1, maxDepth, web)
    return web
