import argparse
import os
from os import listdir

import re

import sys
from pprint import pprint

from sklearn.metrics import mean_squared_error

import indexer
from csv_handling import load_tweet_csv
from tweet import Tweet


def calc_root_mean_squared_error(real, calculated):
    """https://www.kaggle.com/wiki/RootMeanSquaredError"""
    if len(real) != len(calculated) or len(real) == 0:
        raise Exception("Both must have the same length and not zero")
    return mean_squared_error(real, calculated) ** 0.5


def create_dict_from_tweets(tweets):
    dictionary = {}
    for tweet in tweets:
        dictionary[tweet.get_id()] = tweet
    return dictionary


MODE_HUMAN = 1
MODE_MARKDOWN = 2
MODE_MARKDOWN_ALL = 3
printed_header = False
best = {k: {"value": sys.maxint, "file": ""} for k in Tweet.get_all_keys()}


def analyse_csv(result_csv, train_csv, mode=MODE_HUMAN, extended=False):
    calc_tweets = load_tweet_csv(filename=result_csv, use_cache=False, use_pickle=False)
    result_csv = os.path.basename(result_csv)
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

    rmse_single_keys_calc_values = {k: [] for k in Tweet.get_all_keys()}
    rmse_single_keys_real_values = {k: [] for k in Tweet.get_all_keys()}

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

            if extended:
                for key in Tweet.get_all_keys():
                    rmse_single_keys_calc_values[key].append(calc_tweet[key])
                    rmse_single_keys_real_values[key].append(dict_real_tweets[calc_id][key])

    overall = calc_root_mean_squared_error(rmse_real_values, rmse_calc_values)
    kind = calc_root_mean_squared_error(rmse_k_real_values, rmse_k_calc_values)
    sentiment = calc_root_mean_squared_error(rmse_s_real_values, rmse_s_calc_values)
    when = calc_root_mean_squared_error(rmse_w_real_values, rmse_w_calc_values)
    single_keys = {}
    if extended:
        single_keys = {
            k: calc_root_mean_squared_error(rmse_single_keys_real_values[k], rmse_single_keys_calc_values[k])
            for k in Tweet.get_all_keys()
            }
        for key, value in single_keys.iteritems():
            if best[key]["value"] > value:
                best[key]["value"] = value
                best[key]["file"] = result_csv

    if mode == MODE_HUMAN:
        print "--- %s ---" % result_csv
        print "Overall      RMSE: %f" % overall
        print "K(kind)      RMSE: %f" % kind
        print "S(sentiment) RMSE: %f" % sentiment
        print "W(when)      RMSE: %f" % when
        if extended:
            for k in Tweet.get_k_keys():
                print "%s:          RMSE: %f" % (k, single_keys[k])

        print
    elif mode == MODE_MARKDOWN:
        print "| File | Gesamt RMSE | Kind | Sentiment | When |"
        print "|------|------------|------|-----------|------|"
        print "| %s | %f | %f | %f | %f |" % (result_csv, overall, kind, sentiment, when)
        print
    elif mode == MODE_MARKDOWN_ALL:
        global printed_header
        if not printed_header:
            printed_header = True
            print "| File | Gesamt RMSE | Kind | Sentiment | When | " + \
                  " | ".join([k for k in Tweet.get_all_keys()]) + " |"
            print "|------|------------|------|-----------|------|" + "----|" * len(Tweet.get_all_keys())
        to_print = "| %s | %f | %f | %f | %f |" % (result_csv, overall, kind, sentiment, when)
        if extended:
            for k in Tweet.get_all_keys():
                to_print += " %f |" % single_keys[k]
        print to_print


def find_csv_filenames(path_to_dir, suffix=".csv"):
    """https://stackoverflow.com/questions/9234560/find-all-csv-files-in-a-directory-using-python"""
    filenames = listdir(path_to_dir)
    return [os.path.join(path_to_dir, filename) for filename in filenames if filename.endswith(suffix)]


def natural_sort(l):
    """https://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort"""
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def analyse_all(extended, folder=".", test_csv=indexer.TRAININGS_DATA_FILE):
    files = find_csv_filenames(folder)
    if indexer.TRAININGS_DATA_FILE in files:
        files.pop(files.index(indexer.TRAININGS_DATA_FILE))
    if indexer.TEST_DATA_FILE in files:
        files.pop(files.index(indexer.TEST_DATA_FILE))
    for csv_file in natural_sort(files):
        if os.path.isfile(csv_file):
            analyse_csv(csv_file, test_csv, MODE_MARKDOWN_ALL, extended=extended)
            try:
                analyse_csv(csv_file, test_csv, MODE_MARKDOWN_ALL, extended=extended)
            except Exception as e:
                print "Exception(%s) in file: %s " % (e.message, csv_file)
        else:
            print "File does not exist: %s" % csv_file
    print "\n\n"
    print "| Key | Value | File |"
    print "| --- | ----- | ---- |"
    for key in natural_sort(Tweet.get_all_keys()):
        print "| %s | %s | %s |" % (key, best[key]["value"], best[key]["file"])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyse result csv.')
    parser.add_argument('--test_csv', metavar='file', type=str, nargs='?', help='file path to the train csv file',
                        default=indexer.TRAININGS_DATA_FILE, action="store")
    parser.add_argument('--csv_folder', metavar='file', type=str, nargs='?', help='file path to the csv folder',
                        default=".", action="store")
    args = parser.parse_args()
    analyse_all(True, folder=args.csv_folder, test_csv=args.test_csv)
