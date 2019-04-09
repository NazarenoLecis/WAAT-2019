import csv

import matplotlib.pyplot as plt
from nltk import word_tokenize
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from exercise1 import csv2Dict

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


if __name__ == "__main__":
    tfidfVectorizer = TfidfVectorizer(max_features=100,
                                      stop_words='english',
                                      use_idf=True,
                                      tokenizer=word_tokenize,
                                      ngram_range=(1, 2))
    textList = [r['Position'] for r in csv2Dict('data/connections.csv')]
    tfidfMatrix = tfidfVectorizer.fit_transform(textList)
    getBestKForKMeans(tfidfMatrix, maxClusters=30)
