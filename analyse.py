import indexer
from csv_handling import load_tweet_csv, calc_root_mean_squared_error
from tweet import Tweet


def analyse_csv(result_csv, train_csv):
    calc_tweets = load_tweet_csv(filename=result_csv, use_cache=False, use_pickle=False)
    real_tweets = load_tweet_csv(filename=train_csv)

    rmse_calc_values = []
    rmse_real_values = []

    # TODO: slow... maybe: change to two dicts with id as key
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
