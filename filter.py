import multiprocessing

import time

import indices
from normalizer import Normalizer
from tweet import Tweet

unwanted_strings = ["{link}", "@mention", "#weather", "RT:", "RT "]
pool = None


def filter_tweet(tweet):
    for s in unwanted_strings:
        tweet.set_tweet(tweet.get_tweet().replace(s, "").strip())
    return tweet


def filter_field_tweet(normalizer_func, fieldname="tweet"):
    def func(tweet):
        tweet[fieldname] = normalizer_func(tweet[fieldname])
        return tweet

    return func


def filter_normalize_stem(tweet): return tweet.set_tweet(Normalizer.stem(tweet.get_tweet()))


def filter_normalize_lem(tweet): return tweet.set_tweet(Normalizer.lem(tweet.get_tweet()))


def filter_certainty(tweet):
    for key in Tweet.get_all_unknown_keys():
        if tweet[key] > 0.7:
            return None
    return tweet


def filter_spell_checked(tweet): return tweet.set_tweet(Normalizer.autocorrect_sentence(tweet.get_tweet()))


def filter_spell_checked_lem(tweet): return tweet.set_tweet(Normalizer.lem(tweet.get_tweet(), True))


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
    def filter_filtered_stemed(tweets):
        return apply_filters(tweets, filter_tweet, filter_normalize_stem)

    def filter_filtered_lemed(tweets):
        return apply_filters(tweets, filter_tweet, filter_normalize_lem)

    def filter_filtered(tweets): return apply_filters(tweets, filter_tweet)

    def filter_filtered_certain(tweets): return apply_filters(tweets, filter_tweet, filter_certainty)

    def filter_filtered_certain_lemed(tweets):
        return apply_filters(tweets, filter_tweet, filter_certainty, filter_normalize_lem)

    def filter_filtered_spelled_lemed(tweets): return apply_filters(tweets, filter_tweet, filter_spell_checked_lem)

    def filter_filtered_certain_spelled_lemed(tweets): return apply_filters(tweets, filter_tweet,
                                                                            filter_certainty,
                                                                            filter_spell_checked_lem)

    def filter_none(tweets): return tweets
    return {
        indices.INDEX_ALL_FILTERED_STEMED: filter_filtered_stemed,
        indices.INDEX_60k_FILTERED_STEMED: filter_filtered_stemed,
        indices.INDEX_ALL_FILTERED_LEMED: filter_filtered_lemed,
        indices.INDEX_60k_FILTERED_LEMED: filter_filtered_lemed,
        indices.INDEX_ALL_FILTERED: filter_filtered,
        indices.INDEX_60k_FILTERED: filter_filtered,
        indices.INDEX_ALL_FILTERED_CERTAIN: filter_filtered_certain,
        indices.INDEX_60k_FILTERED_CERTAIN: filter_filtered_certain,
        indices.INDEX_ALL_FILTERED_CERTAIN_LEMED: filter_filtered_certain_lemed,
        indices.INDEX_60k_FILTERED_CERTAIN_LEMED: filter_filtered_certain_lemed,
        indices.INDEX_ALL_FILTERED_SPELLED_LEMED: filter_filtered_spelled_lemed,
        indices.INDEX_60k_FILTERED_SPELLED_LEMED: filter_filtered_spelled_lemed,
        indices.INDEX_ALL_FILTERED_CERTAIN_SPELLED_LEMED: filter_filtered_certain_spelled_lemed,
        indices.INDEX_60k_FILTERED_CERTAIN_SPELLED_LEMED: filter_filtered_certain_spelled_lemed,
    }.get(index, filter_none)

