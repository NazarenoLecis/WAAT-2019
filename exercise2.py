import csv
import operator
import random

import matplotlib.pyplot as plt
import pandas as pd

from nltk import word_tokenize
from prettytable import PrettyTable
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import MDS
from sklearn.metrics.pairwise import cosine_similarity


def randomColor():
    return '#%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def plotConnectionGraph(tfidf_matrix, clusters, positions):
    clusterColors = {}
    clusterNames = {}
    for i in range(0, len(clusters)):
        clusterColors[i] = randomColor()
        clusterNames[i] = str(i)
    mds = MDS(n_components=2,
              dissimilarity="precomputed",
              random_state=1)

    dist = 1 - cosine_similarity(tfidf_matrix)
    pos = mds.fit_transform(dist)  # shape (n_components, n_samples)
    xs, ys = pos[:, 0], pos[:, 1]
    df = pd.DataFrame(dict(x=xs,
                           y=ys,
                           label=clusters,
                           title=positions))
    groups = df.groupby('label')
    fig, ax = plt.subplots(figsize=(17, 9))  # set size
    ax.margins(0.05)  # Optional, just adds 5% padding to the autoscaling
    # iterate through groups to layer the plot
    for name, group in groups:
        ax.plot(group.x, group.y,
                marker='o',
                linestyle='',
                ms=12,
                label=clusterNames[name],
                color=clusterColors[name],
                mec='none')
        ax.set_aspect('auto')
        ax.tick_params(axis='x',
                       which='both',
                       bottom='off',
                       top='off',
                       labelbottom='off')
        ax.tick_params(axis='y',
                       which='both',
                       left='off',
                       top='off',
                       labelleft='off')

    ax.legend(numpoints=1)

    for i in range(len(df)):
        ax.text(df.ix[i]['x'], df.ix[i]['y'], df.ix[i]['title'], size=8)

    plt.show()


def clusterDistribution(clusters):
    clusterDict = {}
    for i, c in enumerate(clusters):
        if c in clusterDict.keys():
            clusterDict[c] += 1
        else:
            clusterDict[c] = 1
    prettyTable = PrettyTable(field_names=['Cluster', 'Count'])
    sortedClusters = sorted(clusterDict.items(), key=operator.itemgetter(1), reverse=True)
    for t in sortedClusters:
        prettyTable.add_row(t)
    print prettyTable


def getBestKForKMeans(tfidfMatrix, maxClusters=15):
    sumOfSquaredDistances = []
    K = range(1, maxClusters)
    for k in K:
        km = KMeans(n_clusters=k)
        km = km.fit(tfidfMatrix)
        # inertia_: Sum of squared distances of samples to their closest cluster center.
        sumOfSquaredDistances.append(km.inertia_)
    print sumOfSquaredDistances
    plt.plot(K, sumOfSquaredDistances, 'bx-')
    plt.xlabel('k')
    plt.ylabel('Sum of Squared Distances')
    plt.title('Elbow Method For Optimal k')
    plt.show()


if __name__ == '__main__':
    numClusters = 15
    with open('./data/connections.csv', 'r') as csvFile:
        reader = csv.DictReader(csvFile)
        positions = [row['Position'].decode('utf8') for row in reader]
        tfidfVectorizer = TfidfVectorizer(max_features=100,
                                          stop_words='english',
                                          use_idf=True,
                                          tokenizer=word_tokenize,
                                          ngram_range=(1, 2))
        tfidfMatrix = tfidfVectorizer.fit_transform(positions)
        getBestKForKMeans(tfidfMatrix)
        km = KMeans(n_clusters=numClusters)
        km.fit(tfidfMatrix)
        clusters = km.labels_.tolist()
        print km.predict(tfidfVectorizer.transform(['Post Doc']))
        clusterDistribution(clusters)
        plotConnectionGraph(tfidfMatrix, clusters, positions)
