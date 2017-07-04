import time

from nltk import ngrams

import indices
from tweet import Tweet
import numpy as np


class Termvectorer():
    def __init__(self):
        self._vocabulary = np.array(list(), dtype="string")

    def _get_term_vectors_from_es_and_build_voc(self, index, tweets):
        print "getting termvectors from es"
        termvectors = {}
        empty_vectors = 0
        for tweet in tweets:
            termvectors[tweet.get_id()] = tweet.get_termvector(index)
            if len(termvectors[tweet.get_id()]) == 0:
                empty_vectors += 1
        if empty_vectors > 5:
            print "!!!!! %d Tweets did not return a termvector for index: %s!!!!!" % (empty_vectors, index)

        if len(self._vocabulary) == 0:
            print "building vocabulary"
            tmp_set = set()
            for term_vector in termvectors.values():
                tmp_set.update(term_vector.keys())
            self._vocabulary = np.array(list(tmp_set))
            del tmp_set
            print "vocabulary size %d" % len(self._vocabulary)
        return termvectors

    def create_term_vectors_as_dict(self, index, tweets):
        # type: (str, list) -> dict
        termvectors = self._get_term_vectors_from_es_and_build_voc(index, tweets)

        print "merging term vectors"
        for tweet_id in termvectors:
            termvectors[tweet_id] = np.array(map(lambda x: int(termvectors[tweet_id].get(x, 0)), self._vocabulary),
                                             dtype="int8")
        return termvectors

    def create_term_vectors_as_array(self, index, tweets):
        # type: (str, list) -> np.array
        termvectors = self._get_term_vectors_from_es_and_build_voc(index, tweets)

        print "merging term vectors"
        start = time.time()
        x = np.empty((len(tweets), len(self._vocabulary)), dtype="int8")
        for i in range(len(tweets)):
            x[i] = np.array(map(lambda v: int(termvectors[tweets[i].get_id()].get(v, 0)), self._vocabulary),
                            dtype="int8")
            if i % 1000 == 0:
                print "%d / %d" % (i, len(tweets))
        print "merging term vectors took:", time.time() - start

        return x


def get_binary_feature(feature):
    # type: (float) -> (int, float)
    y = 1 if feature > 0.5 else 0
    return (y, feature) if y == 1 else (y, 1 - feature)


def get_float_feature(feature, digits):
    # type: (float) -> float
    return round(feature, digits)


def merge_numpy_dict_features(features_list, dtype="int8"):
    # type: (list, str) -> np.array
    """Merges multiple dict features to one"""
    if len(features_list) == 0:
        return list()
    length = len(features_list[0])
    amount_of_features = 0
    for f in features_list:
        amount_of_features += len(f.values()[0])
        if len(f) != length:
            raise Exception("Features have to have the same length")
    result = dict()
    for i in features_list[0].keys():
        result[i] = np.array(np.concatenate([f[i] for f in features_list]), dtype=dtype)
    return result


def merge_numpy_array_features(features_list, dtype="int8"):
    # type: (list, str) -> np.array
    """Merges multiple array features to one"""
    if len(features_list) == 0:
        return list()
    length = features_list[0].shape[0]
    amount_of_features = 0
    for f in features_list:
        amount_of_features += f.shape[1]
        if f.shape[0] != length:
            raise Exception("Features have to have the same length")
    result = np.empty((length, amount_of_features), dtype=dtype)
    for i in range(length):
        result[i] = np.concatenate([f[i] for f in features_list])
    return result


def get_ngrams(tweet, n=2):
    """
    Generate ngrams from the tweet text
    :param tweet: the tweet to create ngrams for
    :param n: the length of the ngrams
    :return: a list of ngrams
    """
    return ["".join(dat) for dat in ngrams(tweet.get_tweet(), n)]


if __name__ == '__main__':
    print merge_numpy_array_features([np.array([[1, 1], [2, 2]]), np.array([[3], [4]])])
    print merge_numpy_dict_features([{0: np.array([1, 1]), 2: np.array([2, 2])}, {0: np.array([3]), 2: np.array([4])}])
    tweets = [Tweet({"id": 1}), Tweet({"id": 2})]
    tv = Termvectorer()
    print tv.create_term_vectors_as_dict(indices.INDEX_60k_FILTERED_LEMED, tweets)
    print tv.create_term_vectors_as_array(indices.INDEX_60k_FILTERED_LEMED, tweets)

    # ngrams beispeile
    tweet = Tweet({"tweet": "ich bin hier du bist hier schnabeltier"})
    print get_ngrams(tweet)
    print get_ngrams(tweet, 4)
