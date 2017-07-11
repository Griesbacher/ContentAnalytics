import pprint
import os
import sys
from elasticsearch import Elasticsearch


class Tweet(dict):
    _all_keys = None
    _all_unknown_keys = None
    _es = Elasticsearch()

    def __init__(self, *args, **kwargs):
        super(Tweet, self).__init__(*args, **kwargs)
        if len(self) == 0:
            for k in Tweet.get_all_keys():
                self[k] = 0.0
            self["id"] = -1
            self["tweet"] = ""
        else:
            if "tweet" in self and isinstance(self["tweet"], unicode):
                self["tweet"] = self["tweet"].encode('ascii', 'ignore')

    def __add__(self, other):
        for k in Tweet.get_all_keys():
            self[k] += other[k]

    def __str__(self):
        return pprint.pformat(self).__str__()

    def get_tweet(self):
        # type: (None) -> str
        return self["tweet"]

    def set_tweet(self, tweet):
        # type: (str) -> Tweet
        self["tweet"] = tweet
        return self

    def get_id(self):
        # type: (None) -> int
        return self["id"]

    def set_id(self, new_id):
        # type: (int) -> Tweet
        self["id"] = new_id
        return self

    def normalize(self):
        # type: (Tweet) -> Tweet
        def norm(get_keys_func):
            values = []
            for k in get_keys_func():
                if k in self:
                    values.append(self[k])
                else:
                    values.append(0)

            overall_sum = sum(values)
            if overall_sum == 0:
                return values
            factor = 1.0 / overall_sum
            for v in range(len(values)):
                values[v] *= factor
            return values

        s_values = norm(Tweet.get_s_keys)
        for i in range(len(Tweet.get_s_keys())):
            self[Tweet.get_s_keys()[i]] = s_values[i]

        w_values = norm(Tweet.get_w_keys)
        for i in range(len(Tweet.get_w_keys())):
            self[Tweet.get_w_keys()[i]] = w_values[i]

        for k in Tweet.get_k_keys():
            if self[k] > 1:
                self[k] = 1
            elif self[k] < 0:
                self[k] = 0

        return self

    @staticmethod
    def __does_answer_contain_a_term_vector(answer):
        return "term_vectors" in answer \
               and "tweet" in answer["term_vectors"] \
               and "terms" in answer["term_vectors"]["tweet"]

    def get_termvector(self, index, es=None):
        # type: (str, Elasticsearch) -> dict
        if es is None:
            es = Tweet._es

        answer = es.termvectors(index=index, doc_type='tweet', body={"fields": ["tweet"]}, id=self.get_id())
        if self.__does_answer_contain_a_term_vector(answer):
            term_vector = {key.encode('ascii', 'ignore'): value["term_freq"] for key, value in
                           answer["term_vectors"]["tweet"]["terms"].items()}
            return term_vector
        elif "found" in answer and not answer["found"]:
            from filter import get_filter_from_index
            sys.stdout = open(os.devnull, 'w')
            query = {
                "doc": {"tweet": get_filter_from_index(index)([self])[0].get_tweet()},
                "fields": ["tweet"],
                "positions": False,
                "offsets": False,
                "field_statistics": False,
                "term_statistics": False
            }
            sys.stdout = sys.__stdout__
            answer = self._es.termvectors(index=index, doc_type='tweet', body=query)
            if self.__does_answer_contain_a_term_vector(answer):
                term_vector = {key: value["term_freq"] for key, value in
                               answer["term_vectors"]["tweet"]["terms"].items()}
                return term_vector
        return {}

    def get_tweet_text_from_es(self, index, es=None):
        # type: (str, Elasticsearch) -> str
        if es is None:
            es = Tweet._es

        answer = es.get(index=index, id=self.get_id())
        return answer['tweet']

    @staticmethod
    def get_k_keys():
        # type: (None) -> list
        return ["k1", "k2", "k3", "k4", "k5", "k6", "k7", "k8", "k9", "k10", "k11", "k12", "k13", "k14", "k15"]

    @staticmethod
    def get_s_keys():
        # type: (None) -> list
        return ["s1", "s2", "s3", "s4", "s5"]

    @staticmethod
    def get_w_keys():
        # type: (None) -> list
        return ["w1", "w2", "w3", "w4"]

    @staticmethod
    def get_key_prefixes():
        # type: (None) -> list[str]
        return ["k", "w", "s"]

    @staticmethod
    def get_all_keys():
        # type: (None) -> list
        if Tweet._all_keys is None:
            Tweet._all_keys = []
            Tweet._all_keys.extend(Tweet.get_s_keys())
            Tweet._all_keys.extend(Tweet.get_w_keys())
            Tweet._all_keys.extend(Tweet.get_k_keys())
        return Tweet._all_keys

    @staticmethod
    def get_unknown_k_key():
        return "k7"

    @staticmethod
    def get_unknown_s_key():
        return "s1"

    @staticmethod
    def get_unknown_w_key():
        return "w3"

    @staticmethod
    def get_all_unknown_keys():
        if Tweet._all_unknown_keys is None:
            Tweet._all_unknown_keys = [Tweet.get_unknown_k_key(), Tweet.get_unknown_s_key(), Tweet.get_unknown_w_key()]
        return Tweet._all_unknown_keys
