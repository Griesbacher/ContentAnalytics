from sklearn.linear_model import ridge

import multiprocessing

from csv_handling import load_tweet_csv, write_tweets_to_csv
from filter import get_filter_from_index
from indexer import TRAININGS_DATA_FILE
from indices import INDEX_60k_FILTERED, INDEX_ALL_FILTERED_LEMED
from tweet import Tweet
from elasticsearch import Elasticsearch


class RIDGE:
    def __init__(self, index, es):
        # type: (str, Elasticsearch) -> None
        self._index = index
        self._es = es
        self._classifiers = {key: ridge.RidgeClassifierCV(alphas=(0.1, 0.3, 0.5, 0.7, 0.9)) for key in Tweet.get_all_keys()}
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
    tweet = ridge_classifier.classify(tweet)
    if normalize:
        tweet.normalize()
    return tweet

if __name__ == '__main__':
    normalize = False
    trainigSetSize = 2000  # up to 60000 possible
    index = INDEX_60k_FILTERED
    ridge_classifier = RIDGE(index, Elasticsearch())
    print "RIDGE learning..."
    plain_learn_tweets = load_tweet_csv(TRAININGS_DATA_FILE, use_pickle=False, use_cache=False)[:trainigSetSize]
    filtered_learn_tweets = get_filter_from_index(index)(plain_learn_tweets)
    ridge_classifier.learn(filtered_learn_tweets, verbose=True)
    print "RIDGE classifying..."
    plain_tweets = load_tweet_csv(TRAININGS_DATA_FILE, use_pickle=False, use_cache=False)[60000:]
    filtered_tweets = get_filter_from_index(index)(plain_tweets)

    calculated_tweets = []
    # pool = multiprocessing.Pool()
    # calculated_tweets = pool.map(classify_tweet, filtered_tweets)
    calculated_tweets = map(classify_tweet, filtered_tweets)

    write_tweets_to_csv(calculated_tweets, "{}_ridgeCV_alpha8_{}{}.csv".format(index, trainigSetSize, "_normcls" if normalize else ""))
"""
--- index_60k_filtered_kernel_ridge_1000.csv --- used KernelRidge regression -> very long to process and bad results
Overall      RMSE: 0.300463
K(kind)      RMSE: 0.239059
S(sentiment) RMSE: 0.357953
W(when)      RMSE: 0.408895

index_60k_filtered_ridge_1000.csv --- used RidgeClassifier
Overall      RMSE: 0.235040
K(kind)      RMSE: 0.152526
S(sentiment) RMSE: 0.344202
W(when)      RMSE: 0.310045

--- index_60k_filtered_ridgeCV_1000.csv --- used RidgeClassifierCV(with in-built cross validation) 
Overall      RMSE: 0.227515
K(kind)      RMSE: 0.153039
S(sentiment) RMSE: 0.326880
W(when)      RMSE: 0.298640

--- index_60k_filtered_ridgeCV_1000_normcls.csv 
Overall      RMSE: 0.227132
K(kind)      RMSE: 0.153039
S(sentiment) RMSE: 0.325901
W(when)      RMSE: 0.298231

--- index_60k_filtered_ridgeCV_2000.csv --- 
Overall      RMSE: 0.220596
K(kind)      RMSE: 0.148589 
S(sentiment) RMSE: 0.314031
W(when)      RMSE: 0.293105

--- index_60k_filtered_kernel_ridgeCV_alpha1_2000.csv --- alphas=(0.1, 0.5, 1, 1.2, 1.4)
Overall      RMSE: 0.227092 
K(kind)      RMSE: 0.147440 <-- slightly better
S(sentiment) RMSE: 0.328100 <-- worse
W(when)      RMSE: 0.305521 <-- worse

--- index_60k_filtered_kernel_ridgeCV_alpha2_2000.csv --- alphas=(0.1, 0.3, 0.5, 0.7, 0.9)
Overall      RMSE: 0.230990 
K(kind)      RMSE: 0.148907
S(sentiment) RMSE: 0.335110
W(when)      RMSE: 0.310830

--- index_60k_filtered_kernel_ridgeCV_alpha3_2000.csv --- alphas=(1.5, 1.7, 2.0, 2.2,2.5)
Overall      RMSE:  0.223876
K(kind)      RMSE:  0.146917
S(sentiment) RMSE:  0.322038
W(when)      RMSE:  0.300244

--- index_60k_filtered_ridgeCV_norm_1000.csv
Overall      RMSE: 0.252077 
K(kind)      RMSE: 0.196970
S(sentiment) RMSE: 0.338568
W(when)      RMSE: 0.304108

--- index_60k_filtered_ridgeCV_norm_1000_normcls.csv 
Overall      RMSE: 0.251955
K(kind)      RMSE: 0.196970
S(sentiment) RMSE: 0.338329
W(when)      RMSE: 0.303837
"""
