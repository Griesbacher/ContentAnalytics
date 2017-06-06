from sklearn import svm

from csv_handling import load_tweet_csv, write_tweets_to_csv
from filter import get_filter_from_index
from indexer import TRAININGS_DATA_FILE
from indices import INDEX_60k_FILTERED
from tweet import Tweet


class SVM:
    def __init__(self, index):
        self._index = index
        self._clfs = {key: svm.LinearSVC() for key in Tweet.get_all_keys()}
        self._vocabulary = {}  # term: number

    def getTermVector(self, tweet):
        # TODO
        return []

    def learn(self, tweets):
        # TODO
        # build vocabulary
        for tweet in tweets:
            pass
        # fit svm for each class
        for tweet_class, clf in self._vocabulary.iteritems():
            # clf.fit()
            pass

    def classify(self, tweet):
        term_vectors = self.getTermVector(tweet)
        for tweet_class, clf in self._vocabulary.iteritems():
            class_result = int(self._clfs[tweet_class].predict([term_vectors]).tostring())
            tweet[tweet_class] = class_result
        return tweet


if __name__ == '__main__':
    index = INDEX_60k_FILTERED
    svm_classifier = SVM(index)
    print "SVM learning..."
    plain_learn_tweets = load_tweet_csv(TRAININGS_DATA_FILE, use_pickle=False, use_cache=False)[:60000]
    filtered_learn_tweets = get_filter_from_index(index)(plain_learn_tweets)
    svm_classifier.learn(filtered_learn_tweets)
    print "SVM classifying..."
    plain_tweets = load_tweet_csv(TRAININGS_DATA_FILE, use_pickle=False, use_cache=False)[60000:]
    filtered_tweets = get_filter_from_index(index)(plain_tweets)
    # k = 11
    i = 0
    calculated_tweets = []
    for t in svm_classifier.classify(filtered_tweets):
        calculated_tweets.append(t)
        i += 1
        if i % 1000 == 0:
            print "SVM analysed %d of %d" % (i, len(filtered_tweets))

    write_tweets_to_csv(calculated_tweets, index + "_svm.csv")
