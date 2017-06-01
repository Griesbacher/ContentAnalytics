import indexer
from csv_handling import load_tweet_csv, calc_root_mean_squared_error
from tweet import Tweet


def analyse_csv(result_csv, train_csv):
    calc_tweets = load_tweet_csv(filename=result_csv, use_cache=False, use_pickle=False)
    real_tweets = load_tweet_csv(filename=train_csv)

    dict_calc_tweets = {}
    dict_real_tweets = {}
    for tweet in calc_tweets:
        dict_calc_tweets[tweet.get_id()] = tweet
    for tweet in real_tweets:
        dict_real_tweets[tweet.get_id()] = tweet

    rmse_calc_values = []
    rmse_real_values = []

    rmse_k_calc_values = []
    rmse_k_real_values = []
    rmse_s_calc_values = []
    rmse_s_real_values = []
    rmse_w_calc_values = []
    rmse_w_real_values = []

    for calc_id, calc_tweet in dict_calc_tweets.iteritems():
        if calc_id in dict_real_tweets:
            for key in Tweet.get_k_keys():
                rmse_k_calc_values.append(calc_tweet[key])
                rmse_k_real_values.append(dict_real_tweets[calc_id][key])

            for key in Tweet.get_s_keys():
                rmse_s_calc_values.append(calc_tweet[key])
                rmse_s_real_values.append(dict_real_tweets[calc_id][key])

            for key in Tweet.get_w_keys():
                rmse_w_calc_values.append(calc_tweet[key])
                rmse_w_real_values.append(dict_real_tweets[calc_id][key])

            for key in Tweet.get_all_keys():
                rmse_calc_values.append(calc_tweet[key])
                rmse_real_values.append(dict_real_tweets[calc_id][key])

    print "--- %s ---" % result_csv
    print "Overall      RMSE: %f" % calc_root_mean_squared_error(rmse_real_values, rmse_calc_values)
    print "K(kind)      RMSE: %f" % calc_root_mean_squared_error(rmse_k_real_values, rmse_k_calc_values)
    print "S(sentiment) RMSE: %f" % calc_root_mean_squared_error(rmse_s_real_values, rmse_s_calc_values)
    print "W(when)      RMSE: %f" % calc_root_mean_squared_error(rmse_w_real_values, rmse_w_calc_values)
    print


if __name__ == '__main__':
    for i in range(3, 10, 2):
        analyse_csv(indexer.INDEX_60k_FILTERED_LEMED + "_avg_%d.csv" % i, indexer.TRAININGS_DATA_FILE)
        analyse_csv(indexer.INDEX_60k_FILTERED_LEMED + "_weighted_avg_%d.csv" % i, indexer.TRAININGS_DATA_FILE)
