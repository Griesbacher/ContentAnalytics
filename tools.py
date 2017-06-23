import time

import indices
from tweet import Tweet
import numpy as np


class Termvectorer():
    def __init__(self):
        self._vocabulary = set()

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
            for term_vector in termvectors.values():
                self._vocabulary.update(term_vector.keys())
            self._vocabulary = list(self._vocabulary)
            print "vocabulary size %d" % len(self._vocabulary)
        return termvectors

    def create_term_vectors_as_dict(self, index, tweets):
        # type: (str, list) -> dict
        termvectors = self._get_term_vectors_from_es_and_build_voc(index, tweets)

        print "merging term vectors"
        for tweet_id in termvectors:
            termvectors[tweet_id] = np.array(map(lambda x: float(termvectors[tweet_id].get(x, 0)), self._vocabulary))
        return termvectors

    def create_term_vectors_as_array(self, index, tweets):
        # type: (str, list) -> np.array
        termvectors = self._get_term_vectors_from_es_and_build_voc(index, tweets)

        print "merging term vectors"
        start = time.time()
        x = np.empty((len(tweets), len(self._vocabulary)))
        for i in range(len(tweets)):
            x[i] = np.array(map(lambda v: float(termvectors[tweets[i].get_id()].get(v, 0)), self._vocabulary))
            if i % 1000 == 0:
                print "%d / %d" % (i, len(tweets))
        print "merging term vectors took:", time.time() - start

        return x


def get_binary_feature(feature):
    # type: (float) -> (float, float)
    y = 1.0 if feature > 0.5 else 0.0
    return (y, feature) if y == 1 else (y, 1 - feature)


def get_float_feature(feature, digits):
    # type: (float) -> (float)
    return round(feature, digits)


if __name__ == '__main__':
    tweets = [Tweet({"id": 1}), Tweet({"id": 2})]
    print create_term_vectors_as_dict(indices.INDEX_60k_FILTERED_LEMED, tweets)
    print create_term_vectors_as_array(indices.INDEX_60k_FILTERED_LEMED, tweets)
