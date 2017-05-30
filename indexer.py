import csv
import os
import pickle

from elasticsearch import Elasticsearch

from normalizer import Normalizer
from tweet import Tweet

unwanted_strings = ["{link}", "@mention"]


def load_test_csv(filename, use_pickle=True):
    pickle_file = "csv_data.p"
    if use_pickle and os.path.exists(pickle_file):
        data = pickle.load(open(pickle_file, "rb"))
    else:
        with open(filename, 'rb') as f:
            reader = csv.DictReader(f)
            data = list()
            cast = [
                (["id"], int),
                (Tweet.get_k_keys(), float),
                (Tweet.get_s_keys(), float),
                (Tweet.get_w_keys(), float),
                (["tweet"], str)
            ]
            for row in reader:
                new_tweet = Tweet()
                for key in row:
                    for cast_type, cast_func in cast:
                        if key in cast_type:
                            new_tweet[key] = cast_func(row[key])
                data.append(new_tweet)
    return data


def filter_tweet(tweet):
    for s in unwanted_strings:
        tweet["tweet"] = tweet["tweet"].replace(s, "").strip()
    return tweet


def filter_field_tweet(normalizer_func, fieldname="tweet"):
    def func(tweet):
        tweet[fieldname] = normalizer_func(tweet[fieldname])
        return tweet

    return func


def index_data(tweets, amount, index_name="train"):
    es.indices.delete(index=index_name, ignore=[400, 404])
    i = 0
    for tweet in tweets[:amount]:
        es.index(index=index_name, doc_type='tweet', body=tweet)
        i += 1
        if i % 1000 == 0:
            print "Indexed %i of %i" % (i, amount)


def apply_filters(tweets, *filters):
    for f in filters:
        tweets = map(f, tweets)
    return tweets


INDEX_ALL_FILTERED_STEMED = "index_all_filtered_stemed"
INDEX_ALL_FILTERED_LEMED = "index_all_filtered_lemed"
INDEX_ALL_FILTERED = "index_all_filtered"
INDEX_60k_FILTERED_STEMED = "index_60k_filtered_stemed"
INDEX_60k_FILTERED_LEMED = "index_60k_filtered_lemed"
INDEX_60k_FILTERED = "index_60k_filtered"

normalizer = Normalizer()
es = Elasticsearch()


def index_all_filtered_stemed(tweets):
    tweets = apply_filters(tweets, filter_tweet, filter_field_tweet(normalizer.stem))
    index_data(tweets, len(tweets), INDEX_ALL_FILTERED_STEMED)


def index_all_filtered_lemed(tweets):
    tweets = apply_filters(tweets, filter_tweet, filter_field_tweet(normalizer.lem))
    index_data(tweets, len(tweets), INDEX_ALL_FILTERED_LEMED)


def index_all_filtered(tweets):
    tweets = apply_filters(tweets, filter_tweet)
    index_data(tweets, len(tweets), INDEX_ALL_FILTERED)


def index_60k_filtered_stemed(tweets):
    tweets = apply_filters(tweets, filter_tweet, filter_field_tweet(normalizer.stem))
    index_data(tweets, 60000, INDEX_60k_FILTERED_STEMED)


def index_60k_filtered_lemed(tweets):
    tweets = apply_filters(tweets, filter_tweet, filter_field_tweet(normalizer.lem))
    index_data(tweets, 60000, INDEX_60k_FILTERED_LEMED)


def index_60k_filtered(tweets):
    tweets = apply_filters(tweets, filter_tweet)
    index_data(tweets, 60000, INDEX_60k_FILTERED)


if __name__ == '__main__':
    all_tweets = load_test_csv("train.csv")
    index_60k_filtered_stemed(all_tweets)
