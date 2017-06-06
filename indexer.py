from elasticsearch import Elasticsearch

from csv_handling import load_tweet_csv
from filter import get_filter_from_index
from indices import INDEX_ALL_FILTERED_STEMED, INDEX_ALL_FILTERED_LEMED, INDEX_ALL_FILTERED, INDEX_60k_FILTERED_STEMED, \
    INDEX_60k_FILTERED_LEMED, INDEX_60k_FILTERED, INDEX_60k_FILTERED_CERTAIN_LEMED, INDEX_ALL_FILTERED_CERTAIN_LEMED

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
    index_data(get_filter_from_index(INDEX_ALL_FILTERED_STEMED)(tweets), INDEX_ALL_FILTERED_STEMED)


def index_all_filtered_lemed(tweets):
    index_data(get_filter_from_index(INDEX_ALL_FILTERED_LEMED)(tweets), INDEX_ALL_FILTERED_LEMED)


def index_all_filtered_certain_lemed(tweets):
    index_data(get_filter_from_index(INDEX_ALL_FILTERED_CERTAIN_LEMED)(tweets), INDEX_ALL_FILTERED_CERTAIN_LEMED)


def index_all_filtered(tweets):
    index_data(get_filter_from_index(INDEX_ALL_FILTERED)(tweets), INDEX_ALL_FILTERED)


def index_60k_filtered_stemed(tweets):
    index_data(get_filter_from_index(INDEX_60k_FILTERED_STEMED)(tweets[:60000]), INDEX_60k_FILTERED_STEMED)


def index_60k_filtered_lemed(tweets):
    index_data(get_filter_from_index(INDEX_60k_FILTERED_LEMED)(tweets[:60000]), INDEX_60k_FILTERED_LEMED)


def index_60k_filtered(tweets):
    index_data(get_filter_from_index(INDEX_60k_FILTERED)(tweets[:60000]), INDEX_60k_FILTERED)


def index_60k_filtered_certain_lemed(tweets):
    index_data(get_filter_from_index(INDEX_60k_FILTERED_CERTAIN_LEMED)(tweets[:60000]), INDEX_60k_FILTERED_CERTAIN_LEMED)


if __name__ == '__main__':
    es = Elasticsearch()

    all_tweets = load_tweet_csv(TRAININGS_DATA_FILE)
    index_all_filtered_certain_lemed(all_tweets)
