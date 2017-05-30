import time

import indexer
from elasticsearch import Elasticsearch

from csv_handling import write_tweets_to_csv, load_tweet_csv
from tweet import Tweet


class KNN:
    def __init__(self, index, es_obj):
        self._es = es_obj
        self._index = index

    def get_best_k(self, tweet, k):
        res = self._es.search(index=self._index, body={
            "query": {
                "match": {
                    "tweet": tweet.get_tweet()
                }
            },
            "size": k
        })
        result = dict()
        for hit in res["hits"]["hits"]:
            result[hit["_score"]] = Tweet(hit["_source"])
        return result

    @staticmethod
    def avg(weighted_tweets):
        result_tweet = Tweet()

        for tweet in weighted_tweets.values():
            for key in Tweet.get_all_keys():
                result_tweet[key] += tweet[key]

        if len(weighted_tweets) > 0:
            # TODO: there are some tweets with no match...
            for key in Tweet.get_all_keys():
                result_tweet[key] /= len(weighted_tweets)

        return result_tweet


if __name__ == '__main__':
    index = indexer.INDEX_60k_FILTERED_LEMED
    knn = KNN(index, Elasticsearch())
    plain_tweets = load_tweet_csv(indexer.TRAININGS_DATA_FILE)
    filtered_tweets = indexer.get_filter_from_index(index)(plain_tweets[60000:]) # plain_tweets[60000:] k:5 -> RMSE: 0.192739
    k = 5
    i = 0
    calculated_tweets = []
    for t in filtered_tweets:
        start = time.time()
        calculated_tweet = knn.avg(knn.get_best_k(t, k))
        calculated_tweet.set_id(t.get_id())
        calculated_tweets.append(calculated_tweet)
        i += 1
        if i % 1000 == 0:
            print "KNN analysed %d of %d" % (i, len(filtered_tweets))

    write_tweets_to_csv(calculated_tweets, index + ".csv")
