import networkx as nx
import pylab as plt
from urlparse import urlparse

from crawler import crawler

if __name__ == '__main__':
    url = urlparse('http://info.cern.ch/hypertext/WWW/TheProject.html')
    web = crawler(url)
    webGraph = nx.DiGraph()
    edges = []
    for page in web:
        for link in page.links:
            edges.append((hash(page.address), hash(link)))
    webGraph.add_edges_from(edges)
    nx.draw(webGraph)
    plt.show()
    pageRank = nx.pagerank(webGraph)
    for page in web:
        print page.address, pageRank[hash(page.address)]
