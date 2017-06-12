from elasticsearch import Elasticsearch

from csv_handling import load_tweet_csv
from filter import get_filter_from_index
import indices

TRAININGS_DATA_FILE = "train.csv"
TEST_DATA_FILE = "test.csv"


def index_data(tweets, index_name="train"):
    es.indices.delete(index=index_name, ignore=[400, 404])
    i = 0
    for tweet in tweets:
        es.index(index=index_name, doc_type='tweet', body=tweet)
        i += 1
        if i % 1000 == 0:
            print "Indexed %i of %i" % (i, len(tweets))


def index_all_filtered_stemed(tweets):
    index_data(get_filter_from_index(indices.INDEX_ALL_FILTERED_STEMED)(tweets), indices.INDEX_ALL_FILTERED_STEMED)


def index_all_filtered_lemed(tweets):
    index_data(get_filter_from_index(indices.INDEX_ALL_FILTERED_LEMED)(tweets), indices.INDEX_ALL_FILTERED_LEMED)


def index_all_filtered_certain_lemed(tweets):
    index_data(get_filter_from_index(indices.INDEX_ALL_FILTERED_CERTAIN_LEMED)(tweets),
               indices.INDEX_ALL_FILTERED_CERTAIN_LEMED)


def index_all_filtered(tweets):
    index_data(get_filter_from_index(indices.INDEX_ALL_FILTERED)(tweets), indices.INDEX_ALL_FILTERED)


def index_all_filtered_spelled_lemed(tweets):
    index_data(get_filter_from_index(indices.INDEX_ALL_FILTERED_SPELLED_LEMED)(tweets),
               indices.INDEX_ALL_FILTERED_SPELLED_LEMED)


def index_60k_filtered_stemed(tweets):
    index_data(get_filter_from_index(indices.INDEX_60k_FILTERED_STEMED)(tweets[:60000]),
               indices.INDEX_60k_FILTERED_STEMED)


def index_60k_filtered_lemed(tweets):
    index_data(get_filter_from_index(indices.INDEX_60k_FILTERED_LEMED)(tweets[:60000]),
               indices.INDEX_60k_FILTERED_LEMED)


def index_60k_filtered(tweets):
    index_data(get_filter_from_index(indices.INDEX_60k_FILTERED)(tweets[:60000]), indices.INDEX_60k_FILTERED)


def index_60k_filtered_certain_lemed(tweets):
    index_data(get_filter_from_index(indices.INDEX_60k_FILTERED_CERTAIN_LEMED)(tweets[:60000]),
               indices.INDEX_60k_FILTERED_CERTAIN_LEMED)


def index_60k_filtered_spelled_lemed(tweets):
    index_data(get_filter_from_index(indices.INDEX_60k_FILTERED_SPELLED_LEMED)(tweets[:60000]),
               indices.INDEX_60k_FILTERED_SPELLED_LEMED)


if __name__ == '__main__':
    es = Elasticsearch()

    all_tweets = load_tweet_csv(TRAININGS_DATA_FILE)
    index_all_filtered_certain_lemed(all_tweets)
