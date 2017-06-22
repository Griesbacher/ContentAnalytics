import indices
from tweet import Tweet
import numpy as np

vocabulary = set()


def _get_term_vectors_from_es_and_build_voc(index, tweets):
    print "getting termvectors from es"
    termvectors = {tweet.get_id(): tweet.get_termvector(index) for tweet in tweets}

    global vocabulary
    if len(vocabulary) == 0:
        print "building vocabulary"
        for term_vector in termvectors.values():
            vocabulary.update(term_vector.keys())
        vocabulary = list(vocabulary)
        print "vocabulary size %d" % len(vocabulary)
    return termvectors


def create_term_vectors_as_dict(index, tweets):
    # type: (str, list) -> dict
    termvectors = _get_term_vectors_from_es_and_build_voc(index, tweets)

    print "merging term vectors"
    for tweet_id in termvectors:
        termvectors[tweet_id] = np.array(map(lambda x: float(termvectors[tweet_id].get(x, 0)), vocabulary))
    return termvectors


def create_term_vectors_as_array(index, tweets):
    # type: (str, list) -> np.array
    termvectors = _get_term_vectors_from_es_and_build_voc(index, tweets)

    print "merging term vectors"
    x = None
    for tweet in tweets:
        if x is None:
            x = np.array([np.array(map(lambda x: float(termvectors[tweet.get_id()].get(x, 0)), vocabulary))])
        else:
            x = np.append(x,
                          [np.array(map(lambda x: float(termvectors[tweet.get_id()].get(x, 0)), vocabulary))],
                          axis=0)
    return x


def probability_to_percent(prob):
    # type: (np.array) -> float
    pass


if __name__ == '__main__':
    tweets = [Tweet({"id": 1}), Tweet({"id": 2})]
    print create_term_vectors_as_dict(indices.INDEX_60k_FILTERED_LEMED, tweets)
