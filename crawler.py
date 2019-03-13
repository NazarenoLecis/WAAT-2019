import urllib2
from urlparse import urlparse, urljoin

from bs4 import BeautifulSoup


class Page(object):

    def __init__(self, address, links):
        self.address, self.links = address, links


def crawler(url, iteration=0, maxIterations=2, web=[]):
    print iteration, url.geturl()
    if iteration >= maxIterations:
        return web
    try:
        page = urllib2.urlopen(url.geturl()).read()
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
    web += [Page(url.geturl(), links)]
    for link in links:
        crawler(urlparse(link), iteration + 1, maxIterations, web)
    return web