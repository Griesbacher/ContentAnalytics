import csv
import os
import pickle

from elasticsearch import Elasticsearch

from normalizer import Normalizer
from tweet import Tweet

unwanted_strings = ["{link}", "@mention"]
TRAININGS_DATA_FILE = "train.csv"
csv_cache = None


def load_test_csv(filename, use_pickle=True, use_cache=True):
    global csv_cache
    if use_cache and csv_cache is not None:
        return csv_cache
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
            pickle.dump(data, open(pickle_file, "wb"))
    csv_cache = data
    return data


def filter_tweet(tweet):
    for s in unwanted_strings:
        tweet.set_tweet(tweet.get_tweet().replace(s, "").strip())
    return tweet


def filter_field_tweet(normalizer_func, fieldname="tweet"):
    def func(tweet):
        tweet[fieldname] = normalizer_func(tweet[fieldname])
        return tweet

    return func


def index_data(tweets, index_name="train"):
    es.indices.delete(index=index_name, ignore=[400, 404])
    i = 0
    for tweet in tweets:
        es.index(index=index_name, doc_type='tweet', body=tweet)
        i += 1
        if i % 1000 == 0:
            print "Indexed %i of %i" % (i, len(tweets))


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


def get_filter_from_index(index):
    normalizer = Normalizer()

    def filter_all_filtered_stemed(tweets):
        return apply_filters(tweets, filter_tweet, filter_field_tweet(normalizer.stem))

    def filter_all_filtered_lemed(tweets):
        return apply_filters(tweets, filter_tweet, filter_field_tweet(normalizer.lem))

    def filter_all_filtered(tweets): return apply_filters(tweets, filter_tweet)

    def filter_none(tweets): return tweets

    switcher = {
        INDEX_ALL_FILTERED_STEMED: filter_all_filtered_stemed,
        INDEX_60k_FILTERED_STEMED: filter_all_filtered_stemed,
        INDEX_ALL_FILTERED_LEMED: filter_all_filtered_lemed,
        INDEX_60k_FILTERED_LEMED: filter_all_filtered_lemed,
        INDEX_ALL_FILTERED: filter_all_filtered,
        INDEX_60k_FILTERED: filter_all_filtered,
    }
    return switcher.get(index, filter_none)


def index_all_filtered_stemed(tweets):
    index_data(get_filter_from_index(INDEX_ALL_FILTERED_STEMED)(tweets), INDEX_ALL_FILTERED_STEMED)


def index_all_filtered_lemed(tweets):
    index_data(get_filter_from_index(INDEX_ALL_FILTERED_LEMED)(tweets), INDEX_ALL_FILTERED_LEMED)


def index_all_filtered(tweets):
    index_data(get_filter_from_index(INDEX_ALL_FILTERED)(tweets), INDEX_ALL_FILTERED)


def index_60k_filtered_stemed(tweets):
    index_data(get_filter_from_index(INDEX_60k_FILTERED_STEMED)(tweets[:60000]), INDEX_60k_FILTERED_STEMED)


def index_60k_filtered_lemed(tweets):
    index_data(get_filter_from_index(INDEX_60k_FILTERED_LEMED)(tweets[:60000]), INDEX_60k_FILTERED_LEMED)


def index_60k_filtered(tweets):
    index_data(get_filter_from_index(INDEX_60k_FILTERED)(tweets[:60000]), INDEX_60k_FILTERED)


if __name__ == '__main__':
    es = Elasticsearch()

    all_tweets = load_test_csv(TRAININGS_DATA_FILE)
    index_60k_filtered_lemed(all_tweets)
