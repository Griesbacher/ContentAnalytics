from __future__ import division
import argparse

from analyse import create_dict_from_tweets
from csv_handling import load_tweet_csv, write_tweets_to_csv
from tweet import Tweet
import os

def combine_results(output_path, result_paths, mix):
    """
    Combine the results of multiple classifications to one result file.
    :param output_path: the path of the output file to write to.
    :param result_paths: the paths of the input files result_paths = ['file1.csv', 'file2.csv']
    :param mix: instructions on how to mix the input files into the output file mix = {'k':[0], k1:[1], s:[0], w:[0], w2:[0,1]}
    """
    results = [create_dict_from_tweets(load_tweet_csv(path, False, False)) for path in result_paths]
    final_result = []
    total = len(results[0])
    for i, tweet in enumerate(results[0].values()):
        average_mix('k', mix, results, tweet, Tweet.get_k_keys())
        average_mix('s', mix, results, tweet, Tweet.get_s_keys())
        average_mix('w', mix, results, tweet, Tweet.get_w_keys())
        average_mix_all(mix, results, tweet)
        final_result.append(tweet)
        if i % 100 == 0:
            print "merged {} of {}".format(i, total)
    write_tweets_to_csv(final_result, output_path)


def get_tweet(tweets, id):
    for tweet in tweets:
        if tweet.get_id() == id:
            return tweet


def average_mix_all(mix, results, tweet):
    """
    Mix all tweet classes from the results according to the mix rules
    :param mix: instructions on how to mix the results (which result to use for which class)
    :param results: tweet results to mix
    :param tweet: the (resulting) tweet to mix the values into.
    :return: The tweet object with altered class values
    """
    for key in Tweet.get_all_keys():
        average = 0
        for index in mix[key]:
            average += results[index][tweet.get_id()][key]
        average /= len(mix[key])
        tweet[key] = average


def average_mix(clazz, mix, results, tweet, keys):
    """
        Mix the given tweet classes (keys) from the results according to the mix rules defined by mix[clazz]
        :param clazz: the class to use as mix value
        :param keys: the classes to apply the mix on
        :param mix: instructions on how to mix the results (which result to use for which class)
        :param results: tweet results to mix
        :param tweet: the (resulting) tweet to mix the values into.
        :return: The tweet object with altered class values
    """
    for key in keys:
        average = 0
        for index in mix[clazz]:
            average += results[index][tweet.get_id()][key]
        average /= len(mix[clazz])
        tweet[key] = average


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Combine multiple classification results into one result.'
                                                 'Default for all Classes is 0.'
                                                 'Example:'
                                                 './result_combiner.py --k=0 --s=1 --w=0 --k1=0,1 file1 file2')
    parser.add_argument('file_paths', metavar='file', type=str, nargs='+',
                        help='file path to a result csv file')
    parser.add_argument('-o', metavar='file', type=str,
                        help='path for the output file to merge the inputs into.')
    for clazz in Tweet.get_key_prefixes():
        parser.add_argument('--' + clazz, type=str, metavar='mix',
                            help=clazz + ' class mix, comma separated file indices starting with 0.')
    for clazz in Tweet.get_all_keys():
        parser.add_argument('--' + clazz, type=str, metavar='mix',
                            help=clazz + ' class mix, comma separated file indices starting with 0.')

    args = parser.parse_args()
    result_paths = args.file_paths
    output = args.o if args.o is not None else "combined_" + "_".join(
        [os.path.basename(path).split('.')[0] for path in result_paths]) + ".csv"
    args_dict = vars(args)
    args_dict.pop('file_paths', None)
    args_dict.pop('o', None)
    for key in args_dict:
        args_dict[key] = args_dict[key].split(',') if args_dict[key] is not None else [0]
        for i, val in enumerate(args_dict[key]):
            args_dict[key][i] = int(val)
            if int(val) >= len(result_paths):
                raise ValueError("index for {} is {}, but max allowed is {}".format(key, val, len(result_paths) - 1))

    combine_results(output, result_paths, args_dict)
