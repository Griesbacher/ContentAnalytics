from elasticsearch import Elasticsearch

import indexer
import indices
from csv_handling import write_tweets_to_csv, load_tweet_csv
from filter import get_filter_from_index
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
        # type: (dict) -> Tweet
        result_tweet = Tweet()

        for tweet in weighted_tweets.values():
            for key in Tweet.get_all_keys():
                result_tweet[key] += tweet[key]

        if len(weighted_tweets) > 0:
            for key in Tweet.get_all_keys():
                result_tweet[key] /= len(weighted_tweets)

        return result_tweet

    @staticmethod
    def weighted_avg(weighted_tweets):
        result_tweet = Tweet()
        weights = 0
        for weight, tweet in weighted_tweets.iteritems():
            weights += weight
            for key in Tweet.get_all_keys():
                result_tweet[key] += weight * tweet[key]

        if len(weighted_tweets) > 0:
            for key in Tweet.get_all_keys():
                result_tweet[key] /= weights

        return result_tweet


if __name__ == '__main__':
    plain_tweets = load_tweet_csv(indexer.TRAININGS_DATA_FILE)[60000:]
    for index in indices.get_60k_indices():
        knn = KNN(index, Elasticsearch())
        filtered_tweets = get_filter_from_index(index.replace("_certain", ""))(plain_tweets)
        for k in range(1, 15, 2):
            i = 0
            calculated_tweets_avg = []
            calculated_tweets_weighted_avg = []
            calculated_tweets_weighted_avg_normed = []
            for t in filtered_tweets:
                best_tweets = knn.get_best_k(t, k)
                calculated_tweets_avg.append(knn.avg(best_tweets).set_id(t.get_id()))
                calculated_tweets_weighted_avg.append(knn.weighted_avg(best_tweets).set_id(t.get_id()))
                calculated_tweets_weighted_avg_normed.append(
                    knn.weighted_avg(best_tweets).set_id(t.get_id()).normalize())
                i += 1
                if i % 1000 == 0:
                    print "KNN analysed %d of %d" % (i, len(filtered_tweets))

            write_tweets_to_csv(calculated_tweets_avg, index + "_knn_avg_%d.csv" % k)
            write_tweets_to_csv(calculated_tweets_weighted_avg, index + "_knn_weighted_avg_%d.csv" % k)
            write_tweets_to_csv(calculated_tweets_weighted_avg_normed, index + "_knn_weighted_avg_normed_%d.csv" % k)
