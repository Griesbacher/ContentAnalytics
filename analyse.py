from sklearn.metrics import mean_squared_error

import indexer
from csv_handling import load_tweet_csv
from tweet import Tweet


def calc_root_mean_squared_error(real, calculated):
    """https://www.kaggle.com/wiki/RootMeanSquaredError"""
    if len(real) != len(calculated):
        raise Exception("Both must have the same length")
    return mean_squared_error(real, calculated) ** 0.5


def create_dict_from_tweets(tweets):
    dictionary = {}
    for tweet in tweets:
        dictionary[tweet.get_id()] = tweet
    return dictionary


def analyse_csv(result_csv, train_csv):
    calc_tweets = load_tweet_csv(filename=result_csv, use_cache=False, use_pickle=False)
    real_tweets = load_tweet_csv(filename=train_csv)

    dict_calc_tweets = create_dict_from_tweets(calc_tweets)
    dict_real_tweets = create_dict_from_tweets(real_tweets)

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
    analyse_csv("index_60k_filtered_lemed_weighted_avg_tense_11.csv", indexer.TRAININGS_DATA_FILE)
