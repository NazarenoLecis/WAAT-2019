from __future__ import division

import datetime
import json

import dateutil
import facebook
import matplotlib.pyplot as plt
import numpy as np
import requests
from prettytable import PrettyTable
from textblob import TextBlob

from credentials import FACEBOOK_ACCESS_TOKEN

graph = facebook.GraphAPI(access_token=FACEBOOK_ACCESS_TOKEN, version=3.0)


def serialize(object):
    # restituisce la rappresentazione JSON di un oggetto
    return json.dumps(object, indent=1)


def placeSearch():
    # Ricerca i places vicino 1 Hacker Way in Menlo Park, California.
    places = graph.search(type='place',
                          center='37.4845306,-122.1498183',
                          fields='name,location')
    for place in places['data']:
        print('%s %s' % (place['name'].encode('utf8'), place['location'].get('zip')))


def getPosts():
    # definisco l'oggetto da ricercare: puo' essere un id o il nome di una pagina ad esempio
    user = 'BillGates'
    # recupero l'oggetto utilizzando le API
    profile = graph.get_object(user)
    # Recupero i post associati al profilo recuperato
    posts = graph.get_connections(profile['id'], 'posts')
    print serialize(posts)


def getPostWithPagination():
    # definisco l'oggetto da ricercare: puo' essere un id o il nome di una pagina ad esempio
    user = 'BillGates'
    # seleziono solo i campi da visualizzare
    fields = 'id,category,link,username,talking_about_count'
    # richiedo l'oggetto alle API
    profile = graph.get_object(user, fields=fields)
    # Stampo l'oggetto in formato JSON
    print serialize(profile)
    # Recupero i post
    posts = graph.get_connections(profile['id'], 'posts')
    # Continuo ad iterare sino a quando ci sono pagine
    while True:
        try:
            for post in posts['data']:
                print serialize(post)
                print serialize(graph.get_connections(post['id'], 'comments'))
            # recupero i nuovi post utilizzando i link contenuti nell'oggetto restituito
            posts = requests.get(posts['paging']['next']).json()
            # quando posts['paging'] non ha nessuna chiave 'next'
            # viene lanciata l'eccezzione KeyError e significa che non
            # ci son piu' pagine da iterare
        except KeyError:
            break


def getPostsData(query, count=100):
    # seleziono solo i campi da visualizzare
    fields = 'id,category,link,username,talking_about_count'
    # richiedo l'oggetto alle API
    profile = graph.get_object(query, fields=fields)
    # Recupero i post
    posts = graph.get_connections(profile['id'], 'posts')
    postList = []
    # Continuo ad iterare sino a quando ci sono pagine
    while len(postList) < count:
        try:
            for post in posts['data']:
                if 'message' in post and len(postList) < count:
                    postList.append(post)
            # recupero i nuovi post utilizzando i link contenuti nell'oggetto restituito
            posts = requests.get(posts['paging']['next']).json()
            # quando posts['paging'] non ha nessuna chiave 'next'
            # viene lanciata l'eccezzione KeyError e significa che non
            # ci son piu' pagine da iterare
        except KeyError:
            break
    return postList


def getPostsDataByDate(query, since, until, count=500):
    # seleziono solo i campi da visualizzare
    # richiedo l'oggetto alle API
    # Recupero i post
    posts = graph.get_object(
        "%s/posts" % query,
        since=since,
        until=until,
        limit=100
    )
    postList = []
    # Continuo ad iterare sino a quando ci sono pagine
    while len(postList) < count:
        try:
            for post in posts['data']:
                if 'message' in post and len(postList) < count:
                    postList.append(post)
            # recupero i nuovi post utilizzando i link contenuti nell'oggetto restituito
            posts = requests.get(posts['paging']['next']).json()
            # quando posts['paging'] non ha nessuna chiave 'next'
            # viene lanciata l'eccezzione KeyError e significa che non
            # ci son piu' pagine da iterare
        except KeyError:
            break
    return postList


def getSentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity


def comparativeSentiment(
        entity1="CocaColaUnitedStates",
        entity2="PepsiMaxUSA",
        count=100):
    # recupero il testo dei posts
    entity1Posts = getPostsData(entity1, count=count)
    entity2Posts = getPostsData(entity2, count=count)
    print entity2Posts[0]
    # estraggo solo il testo del post
    entity1Messages = [post['message'] for post in entity1Posts]
    entity2Messages = [post['message'] for post in entity2Posts]
    # calcolo il sentiment per i singoli messaggi
    entity1Sentiment = [getSentiment(message) for message in entity1Messages]
    entity2Sentiment = [getSentiment(message) for message in entity2Messages]
    # imposto la tabella
    prettyTable = PrettyTable(field_names=['Metric', entity1, entity2])
    # numero di posts
    prettyTable.add_row([
        '# Posts',
        len(entity1Sentiment),
        len(entity2Sentiment)
    ])
    # sentiment medio
    prettyTable.add_row([
        'Sentiment AVG',
        '%0.2f' % np.mean(entity1Sentiment),
        '%0.2f' % np.mean(entity2Sentiment)
    ])
    prettyTable.add_row([
        'Sentiment AVG No Neutral',
        "%.2f" % np.mean(filter(lambda x: x != 0, entity1Sentiment)),
        "%.2f" % np.mean(filter(lambda x: x != 0, entity2Sentiment))
    ])
    # calcolo la percentuale di commenti neutrali/positivi/negativi filtrando i valori dalla lista dei sentiment
    prettyTable.add_row([
        'Neutral',
        '%0.2f%%' % (len(filter(lambda x: x == 0.0, entity1Sentiment)) / count * 100),
        '%0.2f%%' % (len(filter(lambda x: x == 0.0, entity2Sentiment)) / count * 100)
    ])
    prettyTable.add_row([
        'Positive',
        '%0.2f%%' % (len(filter(lambda x: x > 0.0, entity1Sentiment)) / count * 100),
        '%0.2f%%' % (len(filter(lambda x: x > 0.0, entity2Sentiment)) / count * 100)
    ])
    prettyTable.add_row([
        'Negative',
        '%0.2f%%' % (len(filter(lambda x: x < 0.0, entity1Sentiment)) / count * 100),
        '%0.2f%%' % (len(filter(lambda x: x < 0.0, entity2Sentiment)) / count * 100)
    ])
    prettyTable.align['Metric'] = 'l'
    print prettyTable
    # Faccio il boxplot dei risultati
    labels = [entity1, entity2]
    plt.figure()
    plt.boxplot(
        [entity1Sentiment, entity2Sentiment],  # passo le due serie di dati
        labels=labels
    )
    plt.show()
    entity1Dates = [
        dateutil.parser.parse(post['created_time'])
        for post in entity1Posts
    ]
    entity2Dates = [
        dateutil.parser.parse(post['created_time'])
        for post in entity2Posts
    ]
    plt.figure()
    plt.plot(entity1Dates, entity1Sentiment)
    plt.plot(entity2Dates, entity2Sentiment)
    plt.legend([entity1, entity2])
    plt.show()


def comparativeSentimentOverTime(
        entity1="donaldtrump",
        entity2="hillaryclinton",
        since='2016-01-01',
        until='2016-02-01',
        count=100):
    # recupero i post nel periodo desiderato
    entity1Posts = getPostsDataByDate(entity1, since, until, count)
    entity2Posts = getPostsDataByDate(entity2, since, until, count)
    # estraggo solo il testo del post
    entity1Messages = [post['message'] for post in entity1Posts]
    entity2Messages = [post['message'] for post in entity2Posts]
    # calcolo il sentiment per i singoli messaggi
    entity1Sentiment = [getSentiment(message) for message in entity1Messages]
    entity2Sentiment = [getSentiment(message) for message in entity2Messages]
    # Estraggo le date dai posts
    entity1Dates = [
        dateutil.parser.parse(post['created_time'])
        for post in entity1Posts
    ]
    print entity1Dates
    entity2Dates = [
        dateutil.parser.parse(post['created_time'])
        for post in entity2Posts
    ]
    # faccio il plot dei risultati
    plt.figure()
    plt.plot(entity1Dates, entity1Sentiment)
    plt.plot(entity2Dates, entity2Sentiment)
    plt.legend([entity1, entity2])
    plt.show()


def groupPostsSentimentByDay(posts):
    messagesPerDay = {}
    for post in posts:
        dateParsed = dateutil.parser.parse(post['created_time']).strftime('%Y-%m-%d')
        sentiment = TextBlob(post['message']).sentiment.polarity
        if dateParsed in messagesPerDay.keys():
            messagesPerDay[dateParsed].append(sentiment)
        else:
            messagesPerDay[dateParsed] = [sentiment]
    return messagesPerDay


def comparativeSentimentAVGPerDay(
        entity1="donaldtrump",
        entity2="hillaryclinton",
        since='2016-01-01',
        until='2016-06-01',
        count=100):
    # recupero i post nel periodo desiderato
    entity1Posts = getPostsDataByDate(entity1, since, until, count)
    entity2Posts = getPostsDataByDate(entity2, since, until, count)
    # Estraggo le date dai posts
    entity1SentimentPerDay = groupPostsSentimentByDay(entity1Posts)
    entity2SentimentPerDay = groupPostsSentimentByDay(entity2Posts)
    entityDates = sorted(list(set(entity1SentimentPerDay.keys()).intersection(set(entity2SentimentPerDay.keys()))))
    entity1Sentiment = [np.mean(entity1SentimentPerDay[date])
                        for date in entityDates]
    entity2Sentiment = [np.mean(entity2SentimentPerDay[date])
                        for date in entityDates
                        if date in entity2SentimentPerDay.keys()]

    # # faccio il plot dei risultati
    plt.figure()
    plt.plot(entityDates, entity1Sentiment)
    plt.plot(entityDates, entity2Sentiment)
    plt.legend([entity1, entity2])
    plt.xticks(entityDates, entityDates, rotation='45')
    plt.show()


if __name__ == '__main__':
    # comparativeSentiment('donaldtrump', 'hillaryclinton')
    comparativeSentimentAVGPerDay(
        'donaldtrump',
        'hillaryclinton',
        since='1 january 2016',
        until='1 march 2016',
        count=1000
    )



