import indices
from tweet import Tweet
import numpy as np

vocabulary = set()


def create_term_vectors(index, tweets):
    # type: (str, list) -> dict
    """Inspired by svm.py"""

    print "getting termvectors from es"
    termvectors = {tweet.get_id(): tweet.get_termvector(index) for tweet in tweets}

    global vocabulary
    if len(vocabulary) == 0:
        print "building vocabulary"
        for term_vector in termvectors.values():
            vocabulary.update(term_vector.keys())
        vocabulary = list(vocabulary)
        print "vocabulary size %d" % len(vocabulary)

    print "merging term vectors"
    for tweet_id in termvectors:
        termvectors[tweet_id] = np.array(map(lambda x: float(termvectors[tweet_id].get(x, 0)), vocabulary))
    return termvectors


def probability_to_percent(prob):
    # type: (np.array) -> float
    pass


if __name__ == '__main__':
    tweets = [Tweet({"id": 1}), Tweet({"id": 2})]
    print (create_term_vectors(indices.INDEX_60k_FILTERED_LEMED, tweets))
