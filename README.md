# WAAT-2019


## Esercitazione 4

Sfruttare la libreria BeautifulSoup per implementare una versione semplificata di un crawler e del PageRank


### Esercizio 1

La prima pagina web mai pubblicata si trova all'indirizzo *http://info.cern.ch/hypertext/WWW/TheProject.html*, utilizzare
Beautifulsoup per fare il crawling del web _primordiale_.

```python

from bs4 import BeautifulSoup
page = urllib2.urlopen('http://info.cern.ch/hypertext/WWW/TheProject.html').read()
soup = BeautifulSoup(page, "html.parser")

```

### Esercizio 2

Partendo dalla pagina iniziale del NewYork Times *https://www.nytimes.com/* recuperare 100 link e calcolare il PageRank 
delle pagine trovate utilizzando questi 100 link (ottenendo quindi una rete con questi 100 link). 

Per calcolare il PageRank utlizzare la libreria *networkx*. Ad esempio calcolando il PageRank della seguente rete:
![alt text](imgs/web-graph2.gif "Esempio page rank")

si ottiene
- 'A': 0.183
- 'C': 0.316
- 'B': 0.328
- 'D': 0.172

Esempio:
```python
    import networkx as nx
    import matplotlib.pyplot as plt
    web = nx.DiGraph()
    web.add_edges_from([
        ('A', 'B'),
        ('B', 'C'),
        ('C', 'D'),
        ('D', 'A'),
        ('C', 'B'),
    ])
    pos = nx.spring_layout(web)
    nx.draw_networkx_labels(web, pos)
    nx.draw(web)
    plt.show()
    print nx.pagerank(web)
```


