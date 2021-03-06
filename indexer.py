from elasticsearch import Elasticsearch

from csv_handling import load_tweet_csv
from filter import get_filter_from_index
import indices

TRAININGS_DATA_FILE = "train.csv"
TEST_DATA_FILE = "test.csv"

indexers = []


def indexer(func):
    """ Registers a function as an indexer. This can be used as decorator. """
    indexers.append(func)
    return func


def index_data(tweets, index_name="train"):
    es.indices.delete(index=index_name, ignore=[400, 404])
    i = 0
    for tweet in tweets:
        es.index(index=index_name, doc_type='tweet', body=tweet, id=tweet.get_id())
        i += 1
        if i % 1000 == 0:
            print "Indexed %i of %i" % (i, len(tweets))


def index_data_filtered(tweets, index, count=None):
    index_data(get_filter_from_index(index)(tweets[:count]), index)


@indexer
def index_all_filtered_stemed(tweets):
    index_data_filtered(tweets, indices.INDEX_ALL_FILTERED_STEMED)


@indexer
def index_all_filtered_lemed(tweets):
    index_data_filtered(tweets, indices.INDEX_ALL_FILTERED_LEMED)


@indexer
def index_all_filtered_certain_lemed(tweets):
    index_data_filtered(tweets, indices.INDEX_ALL_FILTERED_CERTAIN_LEMED)


@indexer
def index_all_filtered(tweets):
    index_data_filtered(tweets, indices.INDEX_ALL_FILTERED)


@indexer
def index_all_filtered_certain(tweets):
    index_data_filtered(tweets, indices.INDEX_ALL_FILTERED_CERTAIN)


@indexer
def index_all_filtered_spelled_lemed(tweets):
    index_data_filtered(tweets, indices.INDEX_ALL_FILTERED_SPELLED_LEMED)


@indexer
def index_all_filtered_stopped_spelled(tweets):
    index_data_filtered(tweets, indices.INDEX_ALL_FILTERED_STOPPED_SPELLED)


@indexer
def index_all_filtered_stopped_spelled_lemed(tweets):
    index_data_filtered(tweets, indices.INDEX_ALL_FILTERED_STOPPED_SPELLED_LEMED)


@indexer
def index_all_filtered_certain_spelled_lemed(tweets):
    index_data_filtered(tweets, indices.INDEX_ALL_FILTERED_CERTAIN_SPELLED_LEMED)


@indexer
def index_all_filtered_certain_stopped_spelled_lemed(tweets):
    index_data_filtered(tweets, indices.INDEX_ALL_FILTERED_CERTAIN_STOPPED_SPELLED_LEMED)


@indexer
def index_all_filtered_ngrammed2(tweets):
    index_data_filtered(tweets, indices.INDEX_ALL_FILTERED_NGRAMMED2)


@indexer
def index_all_filtered_ngrammed4(tweets):
    index_data_filtered(tweets, indices.INDEX_ALL_FILTERED_NGRAMMED4)


@indexer
def index_all_filtered_ngrammed6(tweets):
    index_data_filtered(tweets, indices.INDEX_ALL_FILTERED_NGRAMMED6)


@indexer
def index_all_filtered_ngrammed8(tweets):
    index_data_filtered(tweets, indices.INDEX_ALL_FILTERED_NGRAMMED8)


@indexer
def index_60k_filtered_stemed(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_STEMED, 60000)


@indexer
def index_60k_filtered_lemed(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_LEMED, 60000)


@indexer
def index_60k_filtered(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED, 60000)


@indexer
def index_60k_filtered_certain(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_CERTAIN, 60000)


@indexer
def index_60k_filtered_certain_lemed(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_CERTAIN_LEMED, 60000)


@indexer
def index_60k_filtered_spelled_lemed(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_SPELLED_LEMED, 60000)


@indexer
def index_60k_filtered_stopped_spelled(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_STOPPED_SPELLED, 60000)


@indexer
def index_60k_filtered_stopped_spelled_lemed(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_STOPPED_SPELLED_LEMED, 60000)


@indexer
def index_60k_filtered_certain_spelled_lemed(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_CERTAIN_SPELLED_LEMED, 60000)


@indexer
def index_60k_filtered_certain_stopped_spelled_lemed(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_CERTAIN_STOPPED_SPELLED_LEMED, 60000)


@indexer
def index_60k_filtered_ngrammed2(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_NGRAMMED2, 60000)


@indexer
def index_60k_filtered_ngrammed4(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_NGRAMMED4, 60000)


@indexer
def index_60k_filtered_ngrammed6(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_NGRAMMED6, 60000)


@indexer
def index_60k_filtered_ngrammed8(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_NGRAMMED8, 60000)


@indexer
def index_60k_filtered_stopped_ngrammed4(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_STOPPED_NGRAMMED4, 60000)


@indexer
def index_60k_filtered_spelled_lemed_ngrammed4(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_SPELLED_LEMED_NGRAMMED4, 60000)


@indexer
def index_60k_filtered_stopped_spelled_lemed_ngrammed4(tweets):
    index_data_filtered(tweets, indices.INDEX_60k_FILTERED_STOPPED_SPELLED_LEMED_NGRAMMED4, 60000)


def index_everything(tweets):
    for index in indexers:
        index(tweets)


if __name__ == '__main__':
    es = Elasticsearch()

    all_tweets = load_tweet_csv(TRAININGS_DATA_FILE)
    index_60k_filtered_ngrammed4(all_tweets)
