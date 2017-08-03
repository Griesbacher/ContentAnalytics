import argparse

import indexer
from analyse import create_dict_from_tweets, calc_root_mean_squared_error
from csv_handling import load_tweet_csv
from tweet import Tweet

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyse result csv.')
    parser.add_argument('--test_csv', metavar='file', type=str, nargs='?', help='file path to the train csv file',
                        default=indexer.TRAININGS_DATA_FILE, action="store")
    parser.add_argument('--best_file', metavar='file', type=str, nargs='?', help='file path to the result csv',
                        default="../ergebnisse/combined_best.csv", action="store")
    parser.add_argument('--key', metavar='str', type=str, help='class to inspect',
                        default="s2", action="store")
    parser.add_argument('--tweets', metavar='int', type=str, help='class to inspect',
                        default=5, action="store")
    args = parser.parse_args()
    calc_tweets = load_tweet_csv(filename=args.best_file)
    real_tweets = load_tweet_csv(filename=args.test_csv)

    dict_calc_tweets = create_dict_from_tweets(calc_tweets)
    dict_real_tweets = create_dict_from_tweets(real_tweets)

    errors = list()

    for calc_id, calc_tweet in dict_calc_tweets.iteritems():
        if calc_id in dict_real_tweets:
            # errors.append((calc_id, abs(calc_tweet[args.key] - dict_real_tweets[calc_id][args.key])))
            errors.append(
                (calc_id, calc_root_mean_squared_error([calc_tweet[args.key]], [dict_real_tweets[calc_id][args.key]])))

    sorted_errors = sorted(errors, key=lambda x: x[1])
    print "Class: %s" % Tweet.key_to_text(args.key)
    print "Best:"
    for element in sorted_errors[:args.tweets]:
        print "Error: %s | Expected: %s | Tweet: %s" % (
            element[1], dict_real_tweets[element[0]][args.key], dict_real_tweets[element[0]].get_tweet())
    print "Worst:"
    for element in sorted_errors[-args.tweets:]:
        print "Error: %s | Expected: %s | Tweet: %s" % (
            element[1], dict_real_tweets[element[0]][args.key], dict_real_tweets[element[0]].get_tweet())
