import multiprocessing

import time

import indices
from features import Ngrams
from normalizer import Normalizer
from rating import Rater
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


def filter_ngram2(tweet):
    return tweet.set_tweet(",".join(Ngrams.get_ngrams(tweet, 2)))


def filter_ngram4(tweet):
    return tweet.set_tweet(",".join(Ngrams.get_ngrams(tweet, 4)))


def filter_ngram6(tweet):
    return tweet.set_tweet(",".join(Ngrams.get_ngrams(tweet, 6)))


def filter_ngram8(tweet):
    return tweet.set_tweet(",".join(Ngrams.get_ngrams(tweet, 8)))


def filter_remove_weather_tweets(tweet):
    return None if Rater.is_weather_tweet(tweet)[0] else tweet


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

    @index_filter(indices.INDEX_ALL_FILTERED_NGRAMMED2, indices.INDEX_60k_FILTERED_NGRAMMED2)
    def filter_filtered_ngrammed2(tweets):
        return apply_filters(tweets, filter_tweet, filter_ngram2)

    @index_filter(indices.INDEX_ALL_FILTERED_NGRAMMED4, indices.INDEX_60k_FILTERED_NGRAMMED4)
    def filter_filtered_ngrammed4(tweets):
        return apply_filters(tweets, filter_tweet, filter_ngram4)

    @index_filter(indices.INDEX_ALL_FILTERED_NGRAMMED6, indices.INDEX_60k_FILTERED_NGRAMMED6)
    def filter_filtered_ngrammed6(tweets):
        return apply_filters(tweets, filter_tweet, filter_ngram6)

    @index_filter(indices.INDEX_ALL_FILTERED_NGRAMMED8, indices.INDEX_60k_FILTERED_NGRAMMED8)
    def filter_filtered_ngrammed8(tweets):
        return apply_filters(tweets, filter_tweet, filter_ngram8)

    @index_filter(indices.INDEX_60k_FILTERED_STOPPED_NGRAMMED4)
    def filter_filtered_stopped_ngrammed4(tweets):
        return apply_filters(tweets, filter_tweet, filter_stop_remove, filter_ngram4)

    @index_filter(indices.INDEX_60k_FILTERED_SPELLED_LEMED_NGRAMMED4)
    def filter_filtered_spelled_lemed_ngrammed4(tweets):
        return apply_filters(tweets, filter_tweet, filter_spell_checked_lem, filter_ngram4)

    @index_filter(indices.INDEX_60k_FILTERED_STOPPED_SPELLED_LEMED_NGRAMMED4)
    def filter_filtered_stopped_spelled_lemed_ngrammed4(tweets):
        return apply_filters(tweets, filter_tweet, filter_stop_remove, filter_spell_checked_lem, filter_ngram4)

    def filter_none(tweets):
        return tweets

    return index_filters.get(index, filter_none)
