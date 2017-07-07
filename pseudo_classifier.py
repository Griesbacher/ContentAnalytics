from __future__ import division
from tweet import Tweet
from csv_handling import load_tweet_csv, write_tweets_to_csv

if __name__ == '__main__':
    train_tweets = load_tweet_csv("train.csv")
    test_tweets = train_tweets[60000:]

    key_avg = {k: 0 for k in Tweet.get_all_keys()}
    for tweet in train_tweets:
        for k in Tweet.get_all_keys():
            key_avg[k] += tweet[k]

    for i in Tweet.get_all_keys():
        key_avg[i] /= len(train_tweets)
        print "%s: %f" % (i, key_avg[i])

    for tweet in test_tweets:
        for k in Tweet.get_all_keys():
            tweet[k] = key_avg[k]
        tweet.normalize()

    write_tweets_to_csv(test_tweets, "pseudo.csv")
