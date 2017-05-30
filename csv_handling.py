import csv
import os
import pickle

from sklearn.metrics import mean_squared_error

import indexer
from tweet import Tweet

csv_cache = None


def load_tweet_csv(filename, use_pickle=True, use_cache=True):
    global csv_cache
    if use_cache and csv_cache is not None:
        return csv_cache
    pickle_file = "csv_data.p"
    if use_pickle and os.path.exists(pickle_file):
        data = pickle.load(open(pickle_file, "rb"))
    else:
        with open(filename, 'rb') as f:
            reader = csv.DictReader(f)
            data = list()
            cast = [
                (["id"], int),
                (Tweet.get_k_keys(), float),
                (Tweet.get_s_keys(), float),
                (Tweet.get_w_keys(), float),
                (["tweet"], str)
            ]
            for row in reader:
                new_tweet = Tweet()
                for key in row:
                    for cast_type, cast_func in cast:
                        if key in cast_type:
                            new_tweet[key] = cast_func(row[key])
                data.append(new_tweet)
            if use_pickle:
                pickle.dump(data, open(pickle_file, "wb"))
    if use_cache:
        csv_cache = data
    return data


def write_tweets_to_csv(tweets, filename):
    header = ["id"]
    header.extend(Tweet.get_all_keys())
    with open(filename, 'wb') as testfile:
        csv_writer = csv.writer(testfile)
        csv_writer.writerow(header)
        for t in tweets:
            line = [t.get_id()]
            for key in Tweet.get_all_keys(): line.append(t[key])
            csv_writer.writerow(line)


def calc_root_mean_squared_error(real, calculated):
    """https://www.kaggle.com/wiki/RootMeanSquaredError"""
    if len(real) != len(calculated):
        raise Exception("Both must have the same length")
    return mean_squared_error(real, calculated) ** 0.5


def analyse_csv(result_csv, train_csv):
    calc_tweets = load_tweet_csv(filename=result_csv, use_cache=False, use_pickle=False)
    real_tweets = load_tweet_csv(filename=train_csv)

    rmse_calc_values = []
    rmse_real_values = []

    for ct in calc_tweets:
        for rt in real_tweets:
            if rt.get_id() == ct.get_id():
                for key in Tweet.get_all_keys():
                    rmse_calc_values.append(ct[key])
                    rmse_real_values.append(rt[key])
                continue

    print "RMSE: %f" % calc_root_mean_squared_error(rmse_real_values, rmse_calc_values)


if __name__ == '__main__':
    analyse_csv(indexer.INDEX_60k_FILTERED_LEMED + ".csv", indexer.TRAININGS_DATA_FILE)