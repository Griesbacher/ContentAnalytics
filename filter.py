import multiprocessing

import time

import indices
from normalizer import Normalizer
from tweet import Tweet

unwanted_strings = ["{link}", "@mention", "#weather", "RT:", "RT "]
pool = None

index_filters = {}


def index_filter(*filter_indices):
    """ Registers a function as filter for the given indices. Can be used as decorator. """

    def wrap(func):
        for index in filter_indices:
            index_filters[index] = func
        return func

    return wrap


def filter_tweet(tweet):
    for s in unwanted_strings:
        tweet.set_tweet(tweet.get_tweet().replace(s, "").strip())
    return tweet


def filter_field_tweet(normalizer_func, fieldname="tweet"):
    def func(tweet):
        tweet[fieldname] = normalizer_func(tweet[fieldname])
        return tweet

    return func


def filter_normalize_stem(tweet):
    return tweet.set_tweet(Normalizer.stem(tweet.get_tweet()))


def filter_normalize_lem(tweet):
    return tweet.set_tweet(Normalizer.lem(tweet.get_tweet()))


def filter_stop_remove(tweet):
    return tweet.set_tweet(Normalizer.stopwords_remove(tweet.get_tweet()))


def filter_certainty(tweet):
    for key in Tweet.get_all_unknown_keys():
        if tweet[key] > 0.7:
            return None
    return tweet


def filter_spell_checked(tweet):
    return tweet.set_tweet(Normalizer.autocorrect_sentence(tweet.get_tweet()))


def filter_spell_checked_lem(tweet):
    return tweet.set_tweet(Normalizer.lem(tweet.get_tweet(), True))


def apply_filters(tweets, *filters):
    global pool
    if pool is None:
        pool = multiprocessing.Pool()
    for f in filters:
        start = time.time()
        print "starting: " + f.__name__
        tweets = [x for x in pool.map(f, tweets) if x is not None]
        print "finished: " + f.__name__ + " took %d s" % (time.time() - start)
    return tweets


def get_filter_from_index(index):
    @index_filter(indices.INDEX_ALL_FILTERED_STEMED, indices.INDEX_60k_FILTERED_STEMED)
    def filter_filtered_stemed(tweets):
        return apply_filters(tweets, filter_tweet, filter_normalize_stem)

    @index_filter(indices.INDEX_ALL_FILTERED_LEMED, indices.INDEX_60k_FILTERED_LEMED)
    def filter_filtered_lemed(tweets):
        return apply_filters(tweets, filter_tweet, filter_normalize_lem)

    @index_filter(indices.INDEX_ALL_FILTERED, indices.INDEX_60k_FILTERED)
    def filter_filtered(tweets):
        return apply_filters(tweets, filter_tweet)

    @index_filter(indices.INDEX_ALL_FILTERED_CERTAIN, indices.INDEX_60k_FILTERED_CERTAIN)
    def filter_filtered_certain(tweets):
        return apply_filters(tweets, filter_tweet, filter_certainty)

    @index_filter(indices.INDEX_ALL_FILTERED_CERTAIN_LEMED, indices.INDEX_60k_FILTERED_CERTAIN_LEMED)
    def filter_filtered_certain_lemed(tweets):
        return apply_filters(tweets, filter_tweet, filter_certainty, filter_normalize_lem)

    @index_filter(indices.INDEX_ALL_FILTERED_SPELLED_LEMED, indices.INDEX_60k_FILTERED_SPELLED_LEMED)
    def filter_filtered_spelled_lemed(tweets):
        return apply_filters(tweets, filter_tweet, filter_spell_checked_lem)

    @index_filter(indices.INDEX_ALL_FILTERED_STOPPED_SPELLED, indices.INDEX_60k_FILTERED_STOPPED_SPELLED)
    def filter_filtered_stopped_spelled(tweets):
        return apply_filters(tweets, filter_tweet, filter_stop_remove,
                             filter_spell_checked)

    @index_filter(indices.INDEX_ALL_FILTERED_STOPPED_SPELLED_LEMED, indices.INDEX_60k_FILTERED_STOPPED_SPELLED_LEMED)
    def filter_filtered_stopped_spelled_lemed(tweets):
        return apply_filters(tweets, filter_tweet, filter_stop_remove,
                             filter_spell_checked_lem)

    @index_filter(indices.INDEX_ALL_FILTERED_CERTAIN_STOPPED_SPELLED_LEMED,
                  indices.INDEX_60k_FILTERED_CERTAIN_STOPPED_SPELLED_LEMED)
    def filter_filtered_certain_spelled_lemed(tweets):
        return apply_filters(tweets, filter_tweet,
                             filter_certainty,
                             filter_spell_checked_lem)

    @index_filter(indices.INDEX_ALL_FILTERED_CERTAIN_SPELLED_LEMED, indices.INDEX_60k_FILTERED_CERTAIN_SPELLED_LEMED)
    def filter_filtered_certain_stopped_spelled_lemed(tweets):
        return apply_filters(tweets,
                             filter_tweet,
                             filter_certainty,
                             filter_stop_remove,
                             filter_spell_checked_lem)

    def filter_none(tweets):
        return tweets

    return index_filters.get(index, filter_none)
