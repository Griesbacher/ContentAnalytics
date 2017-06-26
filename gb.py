# gradient boosting machine learning algorithm

import time
from xgboost import XGBClassifier

import indices
from csv_handling import load_tweet_csv, write_tweets_to_csv
from tools import get_binary_feature, Termvectorer
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

    def fit_and_predict(self, train_tweets, test_tweets):
        """reduces the memory a lot"""
        print "fetching termvectors"
        start = time.time()
        x = self._tv.create_term_vectors_as_array(self._train_index, train_tweets)
        test_term_vectors = self._tv.create_term_vectors_as_dict(self._test_index, test_tweets)
        print "finished termvectors", time.time() - start
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
            model.fit(x, np.array(ys), sample_weight=np.array(weights))
            print "predicting %s" % k
            for tweet in test_tweets:
                predict = model.predict_proba(np.array([test_term_vectors[tweet.get_id()]]))
                result[tweet.get_id()][k] = predict[0][1]
        return result.values()


if __name__ == '__main__':
    if platform.system() == "Linux":
        f = open('gb.log', 'w')
        sys.stdout = f

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
            result_tweets = gbm.fit_and_predict(trainings_tweets, testing_tweets)
        else:
            print "starting fit"
            start = time.time()
            gbm.fit(trainings_tweets)
            print "finished fit", time.time() - start
            print "starting predict"
            start = time.time()
            result_tweets = gbm.predict_proba(testing_tweets)
            print "finished fit", time.time() - start
        write_tweets_to_csv(result_tweets, index + "_gb_binary_normalized.csv")

    if platform.system() == "Linux":
        f.close()
