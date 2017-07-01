# gradient boosting machine learning algorithm

import time
from xgboost import XGBClassifier

import indices
from csv_handling import load_tweet_csv, write_tweets_to_csv
from features import get_binary_feature, Termvectorer, merge_numpy_array_features, merge_numpy_dict_features
from rating import Rater
from tweet import Tweet
import numpy as np
import sys
import platform


class GB:
    def __init__(self, train_index, test_index=None):
        self._all_models = {k: XGBClassifier() for k in Tweet.get_all_keys()}
        self._train_index = train_index
        self._test_index = train_index if test_index is None else test_index
        self._tv = Termvectorer()

    def fit(self, tweets):
        print "fetching termvectors"
        start = time.time()
        x = self._tv.create_term_vectors_as_array(self._train_index, tweets)
        print "finished termvectors", time.time() - start
        for k in Tweet.get_all_keys():
            print "fitting %s" % k
            ys = []
            weights = []
            for tweet in tweets:
                y, weight = get_binary_feature(tweet[k])
                ys.append(y)
                weights.append(weight * 100)
            self._all_models[k].fit(x, np.array(ys), sample_weight=np.array(weights))

    def predict_proba(self, tweets):
        term_vectors = self._tv.create_term_vectors_as_dict(self._test_index, tweets)
        print "Starting prediction"
        result = list()
        i = 0
        for tweet in tweets:
            new_tweet = Tweet().set_id(tweet.get_id())
            for k in Tweet.get_all_keys():
                predict = self._all_models[k].predict_proba(np.array([term_vectors[tweet.get_id()]]))
                new_tweet[k] = predict[0][1]
                # binary result
                # predict = self._all_models[k].predict(np.array([term_vectors[tweet.get_id()]]))
                # new_tweet[k] = predict[0]
            result.append(new_tweet.normalize())
            i += 1
            if i % 1000 == 0:
                print "GB analysed %d of %d" % (i, len(tweets))
        return result

    @staticmethod
    def fit_and_predict(train_tweets, test_tweets, create_features_func):
        """reduces the memory a lot"""
        x_train, x_test = create_features_func(train_tweets, test_tweets)

        result = {tweet.get_id(): Tweet().set_id(tweet.get_id()) for tweet in test_tweets}
        for k in Tweet.get_all_keys():
            print "fitting %s" % k
            ys = []
            weights = []
            for tweet in train_tweets:
                y, weight = get_binary_feature(tweet[k])
                ys.append(y)
                weights.append(weight * 100)
            model = XGBClassifier()
            model.fit(x_train, np.array(ys), sample_weight=np.array(weights))
            print "predicting %s" % k
            for tweet in test_tweets:
                predict = model.predict_proba(np.array([x_test[tweet.get_id()]]))
                result[tweet.get_id()][k] = predict[0][1]
        return [r.normalize() for r in result.values()]

    @staticmethod
    def fit_and_predict_multi_class(train_tweets, test_tweets, create_features_func):
        x_train, x_test = create_features_func(train_tweets, test_tweets)

        result = {tweet.get_id(): Tweet().set_id(tweet.get_id()) for tweet in test_tweets}
        print "fitting s"
        model = XGBClassifier()
        x_s = x_train
        for i in range(len(Tweet.get_s_keys()) - 1):
            x_s = np.append(x_s, x_train, axis=0)
        ys = np.empty((len(train_tweets) * len(Tweet.get_s_keys()), 1), dtype="int8")
        weights = np.empty((len(train_tweets) * len(Tweet.get_s_keys()), 1), dtype="int8")
        i = 0
        for k in Tweet.get_s_keys():
            k_index = Tweet.get_s_keys().index(k)
            for tweet in train_tweets:
                ys[i] = k_index
                weights[i] = tweet[k] * 100
                i += 1
        model.fit(x_s, ys, sample_weight=weights)
        print "predicting s"
        for tweet in test_tweets:
            predict = model.predict_proba(np.array([x_test[tweet.get_id()]]))
            i = 0
            for k in Tweet.get_s_keys():
                result[tweet.get_id()][k] = predict[0][i]
                i += 1
        del x_s

        print "fitting w"
        model = XGBClassifier()
        x_w = x_train
        for i in range(len(Tweet.get_w_keys()) - 1):
            x_w = np.append(x_w, x_train, axis=0)
        ys = np.empty((len(train_tweets) * len(Tweet.get_w_keys()), 1), dtype="int8")
        weights = np.empty((len(train_tweets) * len(Tweet.get_w_keys()), 1), dtype="int8")
        i = 0
        for k in Tweet.get_w_keys():
            k_index = Tweet.get_w_keys().index(k)
            for tweet in train_tweets:
                ys[i] = k_index
                weights[i] = tweet[k] * 100
                i += 1
            model.fit(x_w, ys, sample_weight=weights)
        print "predicting w"
        for tweet in test_tweets:
            predict = model.predict_proba(np.array([x_test[tweet.get_id()]]))
            i = 0
            for k in Tweet.get_w_keys():
                result[tweet.get_id()][k] = predict[0][i]
                i += 1
        del x_w

        for k in Tweet.get_k_keys():
            print "fitting %s" % k
            ys = []
            weights = []
            for tweet in train_tweets:
                y, weight = get_binary_feature(tweet[k])
                ys.append(y)
                weights.append(weight * 100)
            model = XGBClassifier()
            model.fit(x_train, np.array(ys), sample_weight=np.array(weights))
            print "predicting %s" % k
            for tweet in test_tweets:
                predict = model.predict_proba(np.array([x_test[tweet.get_id()]]))
                result[tweet.get_id()][k] = predict[0][1]

        return [r.normalize() for r in result.values()]

    def create_wordlist_feature(self, train_tweets, test_tweets):
        print "fetching termvectors"
        start_term = time.time()
        x_train = self._tv.create_term_vectors_as_array(self._train_index, train_tweets)
        x_test = self._tv.create_term_vectors_as_dict(self._test_index, test_tweets)
        print "finished termvectors", time.time() - start_term
        return x_train, x_test

    @staticmethod
    def create_tense_feature(train_tweets, test_tweets):
        print "creating tensevectors"
        start_tense = time.time()
        result = Rater.tense_as_array_feature(train_tweets), Rater.tense_as_dict_feature(test_tweets)
        print "finished tensevectors", time.time() - start_tense
        return result

    @staticmethod
    def create_sentiment_feature(train_tweets, test_tweets):
        print "creating sentimentvectors"
        start_tense = time.time()
        result = Rater.sentiment_as_array_feature(train_tweets), Rater.sentiment_as_dict_feature(test_tweets)
        print "finished sentimentvectors", time.time() - start_tense
        return result

    def create_all_features(self, train_tweets, test_tweets):
        x_train, x_test = self.create_wordlist_feature(train_tweets, test_tweets)
        x_tense_train, x_tense_test = self.create_tense_feature(train_tweets, test_tweets)
        x_sentiment_train, x_sentiment_test = self.create_sentiment_feature(train_tweets, test_tweets)

        x_train = merge_numpy_array_features([x_train, x_tense_train, x_sentiment_train])
        x_test = merge_numpy_dict_features([x_test, x_tense_test, x_sentiment_test])

        return x_train, x_test


if __name__ == '__main__':
    all_tweets = load_tweet_csv("train.csv")
    trainings_tweets = all_tweets[:1000]
    number_of_trainings_tweets = len(trainings_tweets)
    testing_tweets = all_tweets[60000:]
    less_mem = True
    indices_to_test = sys.argv[1:] if len(sys.argv[1:]) > 0 else indices.get_60k_indices()
    print "To test:", indices_to_test
    for index in indices_to_test:
        print "*" * 20 + index + "*" * 20
        gbm = GB(index, index.replace("_60k_", "_all_").replace("_certain", ""))
        if less_mem:
            result_tweets = gbm.fit_and_predict_multi_class(trainings_tweets, testing_tweets,
                                                            gbm.create_all_features)
        else:
            print "starting fit"
            start = time.time()
            gbm.fit(trainings_tweets)
            print "finished fit", time.time() - start
            print "starting predict"
            start = time.time()
            result_tweets = gbm.predict_proba(testing_tweets)
            print "finished fit", time.time() - start
        write_tweets_to_csv(result_tweets,
                            index + "_gb_%d_percent_weighted_multi_class_tense_sentiment_2_normalized.csv" % number_of_trainings_tweets)
