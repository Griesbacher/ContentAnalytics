from indices import INDEX_ALL_FILTERED_STEMED, INDEX_60k_FILTERED_STEMED, INDEX_ALL_FILTERED_LEMED, \
    INDEX_60k_FILTERED_LEMED, INDEX_ALL_FILTERED, INDEX_60k_FILTERED
from normalizer import Normalizer

unwanted_strings = ["{link}", "@mention"]


def filter_tweet(tweet):
    for s in unwanted_strings:
        tweet.set_tweet(tweet.get_tweet().replace(s, "").strip())
    return tweet


def filter_field_tweet(normalizer_func, fieldname="tweet"):
    def func(tweet):
        tweet[fieldname] = normalizer_func(tweet[fieldname])
        return tweet

    return func


def apply_filters(tweets, *filters):
    for f in filters:
        tweets = map(f, tweets)
    return tweets


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
