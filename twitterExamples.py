import re
from collections import Counter

import tweepy
from nltk import word_tokenize
from prettytable import PrettyTable
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from tweepy import OAuthHandler
from textblob import TextBlob

from credentials import TWITTER_ACCESS_TOKEN, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN_SECRET, TWITTER_CONSUMER_KEY

import matplotlib.pyplot as plt

auth = OAuthHandler(
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET
)

auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
twitterAPI = tweepy.API(auth)


def cleanText(tweet):
    '''
    Regular expression that removes links and special characters from tweet.
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w+:\ / \ / \S+)", " ", tweet).split())


def getTweetSentiment(tweet):
    '''
    Calculate the sentiment using TextBlob module
    TextBlog
    '''
    analysis = TextBlob(cleanText(tweet))
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'


def getTweetsSentiment(query, count=10):
    '''
    Given a query returns the tweets
    '''
    tweets = []
    try:
        # calls the API to obtain tweets
        fetchedTweets = tweepy.Cursor(twitterAPI.search, q=query).items(count)
        # parsing the tweets
        for tweet in fetchedTweets:
            parsed_tweet = {}
            # get the tweet text
            parsed_tweet['text'] = tweet.text
            # otteniamo il sentiment associato a quel tweet
            parsed_tweet['sentiment'] = getTweetSentiment(tweet.text)
            # agginugiamo il tweet alla lista assicurandoci che non sia un retweet
            if tweet.retweet_count > 0:
                if parsed_tweet not in tweets:
                    tweets.append(parsed_tweet)
            else:
                tweets.append(parsed_tweet)
        return tweets
    except Exception as e:
        print("Error : %s" % str(e))


def sentimentAnalysisExample():
    tweets = getTweetsSentiment("blockchain", count=100)
    print len(tweets)
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentuale di tweet positivi
    print("Positive tweets percentage: {} %".format(100 * len(ptweets) / len(tweets)))
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentuale di tweet negativi
    print("Negative tweets percentage: {} %".format(100 * len(ntweets) / len(tweets)))
    # stampiamo primi 5 positivi
    print("\n\nPositive tweets:")
    for tweet in ptweets[:5]:
        print(tweet['text'])
    # stampiamo o primi 5 negativi
    print("\n\nNegative tweets:")
    for tweet in ntweets[:5]:
        print(tweet['text'])


def getTweets(query, count=10):
    '''
    Restituisce i tweet data una query particolare
    '''
    tweets = []
    try:
        # chiama la twitter api per cercare i tweet
        fetchedTweets = tweepy.Cursor(twitterAPI.search, q=query).items(count)
        # parsing dei tweet ottenuti
        for tweet in fetchedTweets:
            # agginugiamo il tweet alla lista assicurandoci che non sia un retweet
            if tweet.retweet_count > 0:
                if tweet.text not in tweets:
                    tweets.append(tweet.text)
            else:
                tweets.append(tweet.text)
        return tweets
    except Exception as e:
        print("Error : %s" % str(e))


def topicModeling(query, count=100):
    tweets = getTweets(query, count)
    tf_vectorizer = CountVectorizer(
        max_df=0.95,
        min_df=2,
        max_features=1000,
        stop_words='english'
    )
    tf = tf_vectorizer.fit_transform(tweets)
    tf_feature_names = tf_vectorizer.get_feature_names()
    no_topics = 10
    lda = LatentDirichletAllocation(n_components=no_topics,
                                    max_iter=5,
                                    learning_method='online',
                                    learning_offset=50.,
                                    random_state=0).fit(tf)
    for topic_idx, topic in enumerate(lda.components_):
        print "Topic %d:" % (topic_idx)
        print " ".join([tf_feature_names[i]
                        for i in topic.argsort()[:-10 - 1:-1]])


def countingTweetObjects(query, count):
    tweets = tweepy.Cursor(twitterAPI.search, q=query).items(count)
    status_texts = []
    screen_names = []
    hashtags = []
    for tweet in tweets:
        status_texts.append(tweet.text)
        screen_names += [userMention['screen_name'] for userMention in tweet.entities['user_mentions']]
        hashtags += [hashtag['text'] for hashtag in tweet.entities['hashtags']]
    words = [word for text in status_texts for word in word_tokenize(text)]
    for label, data in [('Word', words),
                        ('Screen Names', screen_names),
                        ('Hashtag', hashtags)
                        ]:
        prettyTable = PrettyTable(field_names=[label, 'Count'])
        counter = Counter(data)
        [prettyTable.add_row(kv) for kv in counter.most_common()[:10]]
        prettyTable.align[label] = 'l'
        prettyTable.align['Count'] = 'r'
        print prettyTable


def tweetsWordFrequency(query, count=10):
    tweets = tweepy.Cursor(twitterAPI.search, q=query).items(count)
    status_texts = []
    screen_names = []
    hashtags = []
    for tweet in tweets:
        status_texts.append(tweet.text)
        screen_names += [userMention['screen_name'] for userMention in tweet.entities['user_mentions']]
        hashtags += [hashtag['text'] for hashtag in tweet.entities['hashtags']]
    words = [word for text in status_texts for word in word_tokenize(text)]

    wordCounts = sorted(Counter(words).values(), reverse=True)
    plt.loglog(wordCounts)
    plt.ylabel("Freq")
    plt.xlabel("Word Rank")
    plt.show()


def retweetHistogram(query, count=10):
    tweets = tweepy.Cursor(twitterAPI.search, q=query).items(count)
    retweets = [
        (tweet.retweet_count,
         tweet.retweeted_status.user.screen_name,
         tweet.text
         )
        for tweet in tweets
        if hasattr(tweet, 'retweeted_status')
    ]
    counts = [count for coun, _, _ in retweets]
    plt.hist(counts)
    plt.title("Retweets")
    plt.xlabel("Bins (number of times retweeted)")
    plt.ylabel("Number of Tweet per Bin")
    plt.show()


def retweetFrequency(query, count=10):
    tweets = tweepy.Cursor(twitterAPI.search, q=query).items(count)
    retweets = [
        (tweet.retweet_count,
         tweet.retweeted_status.user.screen_name,
         tweet.text
         )
        for tweet in tweets
        if hasattr(tweet, 'retweeted_status')
    ]
    prettyPrint = PrettyTable(field_names=['Count', 'Screen', 'Text'])
    [prettyPrint.add_row(row) for row in sorted(retweets, reverse=True)[:5]]
    prettyPrint.max_width['Text'] = 50
    prettyPrint.align = 'l'
    print prettyPrint


if __name__ == '__main__':
    query = "donald trump"
    count = 100
    sentimentAnalysisExample()
    topicModeling(query, count)
    countingTweetObjects(query, count)
    tweetsWordFrequency(query, count)
    retweetFrequency(query, count)
    retweetHistogram(query, count)
