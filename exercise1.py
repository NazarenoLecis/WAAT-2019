import csv

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

from twitterExamples import getTweets, getTweetSentiment, cleanText


def topicModeling(tweets=[]):
    tf_vectorizer = CountVectorizer(
        max_df=0.95,
        min_df=2,
        max_features=1000,
        stop_words='english'
    )
    tf = tf_vectorizer.fit_transform(tweets)
    tf_feature_names = tf_vectorizer.get_feature_names()
    no_topics = 5
    lda = LatentDirichletAllocation(n_components=no_topics,
                                    max_iter=5,
                                    learning_method='online',
                                    learning_offset=50.,
                                    random_state=0).fit(tf)
    for topic_idx, topic in enumerate(lda.components_):
        print "Topic %d:" % (topic_idx)
        print " ".join([tf_feature_names[i]
                        for i in topic.argsort()[:-10 - 1:-1]])


def csv2Dict(path, delimiter=',', quotechar='"'):
    """
    Open a CSV file and return it as a list of dictionaries
    :param path: file path
    :param delimiter: CSV delimiter
    :param quotechar: quote character, double quote is the default
    :return:
    """
    with open(path, 'rb') as csvfile:
        reader = csv.DictReader(
            csvfile,
            delimiter=delimiter,
            quotechar=quotechar
        )
        return [d for d in reader]


def dumpTweets(query, count):
    tweets = getTweets(query=query,
                       count=count)
    filePath = "data/tweets_%s.csv" % query.replace(' ', '_')
    with open(filePath, 'w') as file:
        csvWriter = csv.DictWriter(file,
                                   quotechar='"',
                                   fieldnames=['text'])
        csvWriter.writeheader()
        for tweet in tweets:
            csvWriter.writerow({'text': cleanText(tweet)})
    return filePath


if __name__ == '__main__':
    filePath = 'data/tweets_donald_trump.csv'  # dumpTweets(query="donald trump", count=2000) #
    tweets = [tweet['text'] for tweet in csv2Dict(filePath)]
    print "Found %d tweets" % len(tweets)
    tweetsSentiment = [{'text': tweet, 'sentiment': getTweetSentiment(tweet)}
                       for tweet in tweets]
    positiveTweets = [tweet['text'] for tweet
                      in tweetsSentiment if tweet['sentiment'] == 'positive']
    negativeTweets = [tweet['text'] for tweet
                      in tweetsSentiment if tweet['sentiment'] == 'negative']
    neutralTweets = [tweet['text'] for tweet
                     in tweetsSentiment if tweet['sentiment'] == 'neutral']
    print "Positive Tweets %d" % len(positiveTweets)
    topicModeling(tweets=positiveTweets)
    print "Negative Tweets %d" % len(negativeTweets)
    topicModeling(tweets=negativeTweets)
    print "Neutral Tweets %d" % len(neutralTweets)
    topicModeling(tweets=neutralTweets)
