from os import listdir

import re
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


def analyse_csv(result_csv, train_csv, mode=MODE_HUMAN):
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

    overall = calc_root_mean_squared_error(rmse_real_values, rmse_calc_values)
    kind = calc_root_mean_squared_error(rmse_k_real_values, rmse_k_calc_values)
    sentiment = calc_root_mean_squared_error(rmse_s_real_values, rmse_s_calc_values)
    when = calc_root_mean_squared_error(rmse_w_real_values, rmse_w_calc_values)

    if mode == MODE_HUMAN:
        print "--- %s ---" % result_csv
        print "Overall      RMSE: %f" % overall
        print "K(kind)      RMSE: %f" % kind
        print "S(sentiment) RMSE: %f" % sentiment
        print "W(when)      RMSE: %f" % when
        print
    elif mode == MODE_MARKDOWN:
        print "| File | Gesamt RMSE | Kind | Sentiment | When |"
        print "|------|------------|------|-----------|------|"
        print "| %s | %f | %f | %f | %f |" % (result_csv, overall, kind, sentiment, when)
        print
    elif mode == MODE_MARKDOWN_ALL:
        print "| %s | %f | %f | %f | %f |" % (result_csv, overall, kind, sentiment, when)


def find_csv_filenames(path_to_dir, suffix=".csv"):
    """https://stackoverflow.com/questions/9234560/find-all-csv-files-in-a-directory-using-python"""
    filenames = listdir(path_to_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]


def natural_sort(l):
    """https://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort"""
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def analyse_all():
    files = find_csv_filenames(".")
    files.pop(files.index(indexer.TRAININGS_DATA_FILE))
    files.pop(files.index(indexer.TEST_DATA_FILE))
    for csv_file in natural_sort(files):
        try:
            analyse_csv(csv_file, indexer.TRAININGS_DATA_FILE, MODE_MARKDOWN_ALL)
        except Exception as e:
            print e.message


if __name__ == '__main__':
    analyse_all()
    # analyse_csv("index_60k_filtered_lemed_weighted_avg_tense_11.csv", indexer.TRAININGS_DATA_FILE)
