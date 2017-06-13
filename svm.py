from sklearn import svm

import multiprocessing

from csv_handling import load_tweet_csv, write_tweets_to_csv
from filter import get_filter_from_index
from indexer import TRAININGS_DATA_FILE
from indices import INDEX_60k_FILTERED, INDEX_ALL_FILTERED_LEMED
from tweet import Tweet
from elasticsearch import Elasticsearch


class SVM:
    def __init__(self, index, es):
        # type: (str, Elasticsearch) -> None
        self._index = index
        self._es = es
        self._classifiers = {key: svm.LinearSVC() for key in Tweet.get_all_keys()}
        self._vocabulary = []

    def get_term_vector(self, tweet):
        # type: (Tweet) -> dict
        """
        Retrieve a term vector from elastic search
        :param tweet: the tweet to get the term vector for
        :return: a dictionary with terms as keys and their count as values
        """
        query = {
            "doc": {"tweet": tweet.get_tweet()},
            "fields": [
                "tweet"
            ],
            "positions": False,
            "offsets": False,
            "field_statistics": False,
            "term_statistics": False
        }
        answer = self._es.termvectors(index=self._index, doc_type='tweet', body=query)
        if "term_vectors" in answer and "tweet" in answer["term_vectors"] and "terms" in answer["term_vectors"][
            "tweet"]:
            term_vector = {key: value["term_freq"] for key, value in
                           answer["term_vectors"]["tweet"]["terms"].items()}
            return term_vector
        else:
            return {}

    def get_support_vector(self, term_vector):
        # type: (dict) -> list
        """
        Gets the support vector for a tweet. This may only be called after having called learn(), because
        the vocabulary needs to be built first. Changing the vocabulary later will cause inconsistent support vectors.
        :param term_vector: the termvector to use.
        :return: the supportvector as a list of numbers
        """
        support_vector = map(lambda x: term_vector.get(x, 0), self._vocabulary)
        return support_vector

    def learn(self, tweets, verbose=False):
        # type: (list, bool) -> None
        """
        Learn how to classify tweets with a list of labled example tweets
        :param tweets: the list of tweets to learn from
        :param verbose: print extra information to console, if set to true
        """
        # get all termvectors (for vocabulary building)
        if verbose:
            print "Creating term vectors"
        termvectors = {tweet.get_id(): self.get_term_vector(tweet) for tweet in tweets}

        # build vocabulary
        if verbose:
            print "Building vocabulary"
        vocabulary = set()
        for term_vector in termvectors.values():
            vocabulary.update(term_vector.keys())
        self._vocabulary = list(vocabulary)

        # build the support vectors
        if verbose:
            print "Creating support vectors"
        for tweet_id in termvectors:
            termvectors[tweet_id] = self.get_support_vector(termvectors[tweet_id])

        # fit each svm classifier
        for tweet_class, classifier in self._classifiers.iteritems():
            if verbose:
                print "Preparing classifier for for {tweet_class}".format(tweet_class=tweet_class)
            fit_support_vectors = []
            fit_classes = []
            for tweet in tweets:
                fit_support_vectors.append(termvectors[tweet.get_id()])
                fit_classes.append(1 if tweet[tweet_class] > 0.5 else 0)
            classifier.fit(fit_support_vectors, fit_classes)

    def classify(self, tweet):
        """
        Classifies a tweet and updates its class values accordingly
        :param tweet: the tweet to classify
        :return: the same tweet with updated classes
        """
        # type: (Tweet) -> Tweet
        term_vectors = self.get_support_vector(self.get_term_vector(tweet))
        for tweet_class, clf in self._classifiers.iteritems():
            class_result = int(self._classifiers[tweet_class].predict([term_vectors]).tolist()[0])
            tweet[tweet_class] = class_result
        return tweet


def classify_tweet(tweet):
    tweet = svm_classifier.classify(tweet)
    if normalize:
        tweet.normalize()
    return tweet


if __name__ == '__main__':
    normalize = True
    trainigSetSize = 1000  # up to 60000 possible
    index = INDEX_60k_FILTERED
    svm_classifier = SVM(index, Elasticsearch())
    print "SVM learning..."
    plain_learn_tweets = load_tweet_csv(TRAININGS_DATA_FILE, use_pickle=False, use_cache=False)[:trainigSetSize]
    filtered_learn_tweets = get_filter_from_index(index)(plain_learn_tweets)
    svm_classifier.learn(filtered_learn_tweets, verbose=True)
    print "SVM classifying..."
    plain_tweets = load_tweet_csv(TRAININGS_DATA_FILE, use_pickle=False, use_cache=False)[60000:]
    filtered_tweets = get_filter_from_index(index)(plain_tweets)

    calculated_tweets = []
    pool = multiprocessing.Pool()
    calculated_tweets = pool.map(classify_tweet, filtered_tweets)

    write_tweets_to_csv(calculated_tweets,
                        "{}_svm_{}{}.csv".format(index, trainigSetSize, "_normcls" if normalize else ""))

"""
--- index_60k_filtered_svm_1000.csv --- with 1000 training tweets and without normalizing the classes
Overall      RMSE: 0.237392
K(kind)      RMSE: 0.154598
S(sentiment) RMSE: 0.347026
W(when)      RMSE: 0.312999

--- index_60k_filtered_svm_1000_normcls.csv --- with 1000 training tweets and normalizing the classes
Overall      RMSE: 0.234081
K(kind)      RMSE: 0.154598
S(sentiment) RMSE: 0.336055 <- slight improvement caused by class normalization
W(when)      RMSE: 0.312999

--- index_60k_filtered_svm_2000_normcls.csv --- with 2000 training tweets and normalizing the classes
Overall      RMSE: 0.230057 <- overall improvement
K(kind)      RMSE: 0.151032
S(sentiment) RMSE: 0.324437
W(when)      RMSE: 0.316928 <- this however got worse!

--- index_60k_filtered_svm_5000_normcls.csv --- with 5000 training tweets and normalizing the classes
Overall      RMSE: 0.224530
K(kind)      RMSE: 0.146955 <- still improvement! This seems to work well!
S(sentiment) RMSE: 0.314136
W(when)      RMSE: 0.313282 <- at least not worse...

--- index_60k_filtered_svm_10000_normcls.csv --- with 10000 training tweets and normalizing the classes
Overall      RMSE: 0.221429
K(kind)      RMSE: 0.145574
S(sentiment) RMSE: 0.306823
W(when)      RMSE: 0.311512

--- index_60k_filtered_svm_20000_normcls.csv --- with 20000 training tweets and normalizing the classes
Overall      RMSE: 0.217452
K(kind)      RMSE: 0.144079
S(sentiment) RMSE: 0.299260
W(when)      RMSE: 0.306466
"""
