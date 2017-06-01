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

    @staticmethod
    def weighted_avg(weighted_tweets):
        result_tweet = Tweet()
        weights = 0
        for weight, tweet in weighted_tweets.iteritems():
            weights += weight
            for key in Tweet.get_all_keys():
                result_tweet[key] += weight * tweet[key]

        if len(weighted_tweets) > 0:
            # TODO: there are some tweets with no match...
            for key in Tweet.get_all_keys():
                result_tweet[key] /= weights

        return result_tweet


if __name__ == '__main__':
    index = indexer.INDEX_60k_FILTERED_LEMED
    knn = KNN(index, Elasticsearch())
    plain_tweets = load_tweet_csv(indexer.TRAININGS_DATA_FILE, use_pickle=False, use_cache=False)[60000:]
    filtered_tweets = indexer.get_filter_from_index(index)(plain_tweets)
    k = 11
    i = 0
    calculated_tweets_avg = []
    calculated_tweets_weighted_avg = []
    for t in filtered_tweets:
        best_tweets = knn.get_best_k(t, k)
        calculated_tweets_avg.append(knn.avg(best_tweets).set_id(t.get_id()))
        calculated_tweets_weighted_avg.append(knn.weighted_avg(best_tweets).set_id(t.get_id()))
        i += 1
        if i % 1000 == 0:
            print "KNN analysed %d of %d" % (i, len(filtered_tweets))

    write_tweets_to_csv(calculated_tweets_avg, index + "_avg_%d.csv" % k)
    write_tweets_to_csv(calculated_tweets_weighted_avg, index + "_weighted_avg_%d.csv" % k)

"""
--- index_60k_filtered_lemed_avg_3.csv ---
Overall      RMSE: 0.203439
K(kind)      RMSE: 0.174443
S(sentiment) RMSE: 0.242963
W(when)      RMSE: 0.245808

--- index_60k_filtered_lemed_weighted_avg_3.csv ---
Overall      RMSE: 0.202855
K(kind)      RMSE: 0.173877
S(sentiment) RMSE: 0.242193
W(when)      RMSE: 0.245370

--- index_60k_filtered_lemed_avg_5.csv ---
Overall      RMSE: 0.192739
K(kind)      RMSE: 0.164361
S(sentiment) RMSE: 0.230867
W(when)      RMSE: 0.234439

--- index_60k_filtered_lemed_weighted_avg_5.csv ---
Overall      RMSE: 0.191891
K(kind)      RMSE: 0.163568
S(sentiment) RMSE: 0.229803
W(when)      RMSE: 0.233649

--- index_60k_filtered_lemed_avg_7.csv ---
Overall      RMSE: 0.187786
K(kind)      RMSE: 0.159906
S(sentiment) RMSE: 0.225043
W(when)      RMSE: 0.228885

--- index_60k_filtered_lemed_weighted_avg_7.csv ---
Overall      RMSE: 0.186858
K(kind)      RMSE: 0.159036
S(sentiment) RMSE: 0.223846
W(when)      RMSE: 0.228069

--- index_60k_filtered_lemed_avg_9.csv ---
Overall      RMSE: 0.185497
K(kind)      RMSE: 0.157653
S(sentiment) RMSE: 0.222578
W(when)      RMSE: 0.226551

--- index_60k_filtered_lemed_weighted_avg_9.csv ---
Overall      RMSE: 0.184493
K(kind)      RMSE: 0.156741
S(sentiment) RMSE: 0.221260
W(when)      RMSE: 0.225615

--- index_60k_filtered_lemed_avg_11.csv ---
Overall      RMSE: 0.184179
K(kind)      RMSE: 0.156396
S(sentiment) RMSE: 0.221299
W(when)      RMSE: 0.224924

--- index_60k_filtered_lemed_weighted_avg_11.csv ---
Overall      RMSE: 0.183105
K(kind)      RMSE: 0.155424
S(sentiment) RMSE: 0.219887
W(when)      RMSE: 0.223918
"""