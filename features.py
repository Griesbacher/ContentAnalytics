import string
import time

import numpy as np
from elasticsearch import Elasticsearch
from nltk import ngrams

import indices
from csv_handling import load_tweet_csv


class Termvectorer:
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


class TfIdf:
    _es = Elasticsearch()

    @staticmethod
    def get_feature_as_dict(train_tweets, test_tweets, index, es=None):
        # type: (list, list,str, Elasticsearch) -> dict
        if es is None:
            es = TfIdf._es
        from filter import get_filter_from_index
        test_tweets = get_filter_from_index(index)(test_tweets)
        train_tweet_indices = [tweet.get_id() for tweet in train_tweets]
        result_dict = {tweet.get_id(): np.empty(len(train_tweets), dtype="uint8") for tweet in test_tweets}
        i = 0
        for tweet in test_tweets:
            res = es.search(index=index,
                            body={
                                "query": {
                                    "bool": {
                                        "should": {
                                            "match": {
                                                "tweet": tweet.get_tweet()
                                            }
                                        },
                                        "filter": {
                                            "terms": {
                                                "id": train_tweet_indices
                                            }
                                        }
                                    }
                                }
                            }
                            )
            for hit in res["hits"]["hits"]:
                result_dict[tweet.get_id()][train_tweet_indices.index(hit["_source"]["id"])] = \
                    min(hit["_score"] * 10, 255)
            i += 1
            if i % 1000 == 0:
                print "Got %d from ES as dict" % i
        return result_dict

    @staticmethod
    def get_feature_as_array(train_tweets, test_tweets, index, es=None):
        # type: (list, list,str, Elasticsearch) -> np.array
        if es is None:
            es = TfIdf._es
        from filter import get_filter_from_index
        test_tweets = get_filter_from_index(index)(test_tweets)
        train_tweet_indices = [tweet.get_id() for tweet in train_tweets]
        result_array = np.empty((len(test_tweets), len(train_tweets)), dtype="uint8")
        i = 0
        for tweet in test_tweets:
            res = es.search(index=index,
                            body={
                                "query": {
                                    "bool": {
                                        "should": {
                                            "match": {
                                                "tweet": tweet.get_tweet()
                                            }
                                        },
                                        "filter": {
                                            "terms": {
                                                "id": train_tweet_indices
                                            }
                                        }
                                    }
                                }
                            }
                            )
            for hit in res["hits"]["hits"]:
                result_array[i][train_tweet_indices.index(hit["_source"]["id"])] = \
                    min(hit["_score"] * 10, 255)
            i += 1
            if i % 1000 == 0:
                print "Got %d from ES as array" % i
        return result_array


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


class Ngrams(object):
    def __init__(self, n, vocabulary=None):
        self._n = n
        self._vocabulary = np.array(list() if vocabulary is None else vocabulary, dtype="string")

    def _get_ngrams_and_build_voc(self, index, tweets):
        if len(self._vocabulary) == 0:
            result = {}
            tmp_set = set()
            for tweet in tweets:
                if self._n > 4:
                    ng = tweet.get_tweet_text_from_es(index).lower()
                else:
                    ng = tweet.get_tweet_text_from_es(index)
                tmp_set.update(ng.split(','))
                result[tweet.get_id()] = (ng.split(','))
            if self._n > 2:
                print "Vocabulary size before shrinking: %d" % len(tmp_set)
                printable = [c for c in string.punctuation + string.digits + string.whitespace]
                numbers = set()
                for gram in tmp_set:
                    if any(char in printable for char in gram):
                        numbers.add(gram)
                for number in numbers:
                    tmp_set.remove(number)
            self._vocabulary = np.array(list(tmp_set))
            print "Vocabulary size: %d" % len(self._vocabulary)
            return result
        else:
            return {tweet.get_id(): Ngrams.get_ngrams(tweet, self._n) for tweet in tweets}

    def create_ngrams_as_dict(self, index, tweets):
        """
        Creates ngrams from a list of tweets. If the vocabulary has not been built or provieded, the vocabulary is
        built and the ngrams are taken from the es index. Otherwise, new ngrams are generated from the
        provided tweet texts. If the vocabulary is already built , the tweets must be filtered with the same
        filters as the index, to obtain sensible results, since this method does not perform any fitlering.
        :param index: the es index
        :param tweets: a list of tweets to get the ngrams for
        :return: a dict with tweet ids as keys and ready to use ngram vectors as values
        """
        result = {}
        ngrams = self._get_ngrams_and_build_voc(index, tweets)
        for id in ngrams:
            ngram_count = {}
            for ngram in ngrams[id]:
                ngram_count[ngram] = ngram_count.get(ngram, 0) + 1
            ngram_dict = np.array(map(lambda v: int(ngram_count.get(v, 0)), self._vocabulary), dtype="int8")
            result[id] = ngram_dict
        return result

    def create_ngrams_as_array(self, index, tweets):
        """
        Does the same thing as create_ngrams_as_dict, but returns an array instead of a dict.
        """
        ngram_dict = self.create_ngrams_as_dict(index, tweets)
        x = np.empty((len(tweets), len(self._vocabulary)), dtype="int8")
        for i in range(len(tweets)):
            x[i] = ngram_dict[tweets[i].get_id()]
        return x

    @staticmethod
    def get_ngrams(tweet, n=2):
        """
        Generate ngrams from the tweet text
        :param tweet: the tweet to create ngrams for
        :param n: the length of the ngrams
        :return: a list of ngrams
        """
        if n > 4:
            return ["".join(dat) for dat in ngrams(tweet.get_tweet().lower(), n)]
        else:
            return ["".join(dat) for dat in ngrams(tweet.get_tweet(), n)]


if __name__ == '__main__':
    # TfIdf example
    # print TfIdf.get_feature_as_array(
    #     [Tweet({"id": 1}), Tweet({"id": 2})],
    #     [Tweet({"id": 9, "tweet": "@mention good morning sunshine rhode island"}), ],
    #     indices.INDEX_60k_FILTERED
    # )
    # print TfIdf.get_feature_as_dict(
    #     [Tweet({"id": 1}), Tweet({"id": 2})],
    #     [Tweet({"id": 9, "tweet": "@mention good morning sunshine rhode island"}), ],
    #     indices.INDEX_60k_FILTERED
    # )

    # Merging Features example
    # print merge_numpy_array_features([np.array([[1, 1], [2, 2]]), np.array([[3], [4]])])
    # print merge_numpy_dict_features([{0: np.array([1, 1]), 2: np.array([2, 2])}, {0: np.array([3]), 2: np.array([4])}])

    # Termvector example
    # tweets = [Tweet({"id": 1}), Tweet({"id": 2})]
    # tv = Termvectorer()
    # print tv.create_term_vectors_as_dict(indices.INDEX_60k_FILTERED, tweets)
    # print tv.create_term_vectors_as_array(indices.INDEX_60k_FILTERED, tweets)

    # ngrams beispeile
    # tweet = Tweet({"tweet": "ich bin hier du bist hier schnabeltier"})
    # print Ngrams.get_ngrams(tweet)
    # print Ngrams.get_ngrams(tweet, 4)

    # tweets = [Tweet({"tweet": "lalalalele", "id": 1}), Tweet({"tweet": "lale", "id": 2})]
    # ngrammer = Ngrams(2, ["la", "le", "al", "el"])
    # print ngrammer.create_ngrams_as_dict(indices.INDEX_60k_FILTERED_NGRAMMED2, tweets)
    #
    # ngrammer = Ngrams(3, ["lal", "ala", "ale", "ele"])
    # print ngrammer.create_ngrams_as_array(indices.INDEX_60k_FILTERED_NGRAMMED2, tweets)
    #
    # tweets = [Tweet({"id": 1}), Tweet({"id": 2})]
    # ngrammer = Ngrams(3)
    # print ngrammer.create_ngrams_as_dict(indices.INDEX_60k_FILTERED_NGRAMMED2, tweets)

    tweets = load_tweet_csv("train.csv")[:2]
    print tweets
    ngrammer = Ngrams(2)
    print ngrammer.create_ngrams_as_dict(indices.INDEX_60k_FILTERED_NGRAMMED2, tweets)
    # not quite right. the tweets should be filtered first, like the index. but that is not
    # possible here, since there are cyclic imports everywhere.
    print ngrammer.create_ngrams_as_dict(indices.INDEX_60k_FILTERED_NGRAMMED2, tweets)
