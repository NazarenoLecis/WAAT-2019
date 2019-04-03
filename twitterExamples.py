from collections import Counter

import matplotlib.pyplot as plt
import tweepy
from nltk import word_tokenize, re
from prettytable import PrettyTable
from textblob import TextBlob
from tweepy import OAuthHandler

from credentials import TWITTER_ACCESS_TOKEN, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN_SECRET, TWITTER_CONSUMER_KEY

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
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(https?\S+)", " ", tweet).split())


def getTweetSentiment(tweet):
    '''
    Calculate the sentiment using TextBlob module
    TextBlog
    '''
    text = cleanText(tweet)
    print text
    analysis = TextBlob(text)
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
            # get the sentiment for the tweet's text
            parsed_tweet['sentiment'] = getTweetSentiment(tweet.text)
            # add the tweet to our list and avoid retweets
            if tweet.retweet_count > 0:
                if parsed_tweet not in tweets:
                    tweets.append(parsed_tweet)
            else:
                tweets.append(parsed_tweet)
        return tweets
    except Exception as e:
        print("Error : %s" % str(e))


def sentimentAnalysisExample(query="blockchain", count=100):
    tweets = getTweetsSentiment(query, count=count)
    print len(tweets)
    ptweets = [tweet for tweet in tweets
               if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    print("Positive tweets percentage: {} %".format(100 * len(ptweets) / len(tweets)))
    ntweets = [tweet for tweet in tweets
               if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    print("Negative tweets percentage: {} %".format(100 * len(ntweets) / len(tweets)))
    # print the first five positive tweets
    print("\n\nPositive tweets:")
    for tweet in ptweets[:5]:
        print(tweet['text'])
    # print the first five negative tweets
    print("\n\nNegative tweets:")
    for tweet in ntweets[:5]:
        print(tweet['text'])


def getTweets(query, count=10):
    '''
    Restituisce i tweet data una query particolare
    '''
    tweets = []
    try:
        # calls the API to obtain tweets
        fetchedTweets = tweepy.Cursor(twitterAPI.search, q=query).items(count)
        # parsing the tweets
        for tweet in fetchedTweets:
            # add the tweet to our list and avoid retweets
            if tweet.retweet_count > 0:
                if tweet.text not in tweets:
                    tweets.append(tweet.text)
            else:
                tweets.append(tweet.text)
        return tweets
    except Exception as e:
        print("Error : %s" % str(e))


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
    counts = [count for count, _, _ in retweets]
    plt.hist(counts)
    plt.title("Retweets")
    plt.xlabel("Bins (number of times retweeted)")
    plt.ylabel("Number of Tweet per Bin")
    plt.show()


def retweetFrequency(query, count=10):
    tweets = tweepy.Cursor(twitterAPI.search, q=query).items(count)
    uniqueTweets = set()
    retweets = []
    for tweet in tweets:
        if hasattr(tweet, 'retweeted_status'):
            if tweet.text not in uniqueTweets:
                retweets += [
                    (tweet.retweet_count,
                     tweet.retweeted_status.user.screen_name,
                     tweet.text
                     )]
                uniqueTweets.add(tweet.text)
    prettyPrint = PrettyTable(field_names=['Count', 'Screen', 'Text'])
    [prettyPrint.add_row(row) for row in sorted(retweets, reverse=True)[:5]]
    prettyPrint.max_width['Text'] = 50
    prettyPrint.align = 'l'
    print prettyPrint


if __name__ == '__main__':
    query = "donald trump"
    count = 100
    sentimentAnalysisExample(query, count)
    countingTweetObjects(query, count)
    tweetsWordFrequency(query, count)
    retweetFrequency(query, count)
    retweetHistogram(query, count)
