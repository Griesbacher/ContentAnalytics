import csv
import os
import pickle

from indices import get_all_indices
from tweet import Tweet

csv_cache = dict()


def load_tweet_csv(filename, use_pickle=True, use_cache=True):
    # type: (str, bool, bool) -> list
    global csv_cache
    if use_cache and filename in csv_cache:
        return csv_cache[filename]
    pickle_file = filename + ".p"
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
        csv_cache[filename] = data
    return data


def write_tweets_to_csv(tweets, filename):
    # type: (list, str) -> None
    if tweets is None or len(tweets) == 0 or filename == "":
        return
    print "Writing %d tweets to %s" % (len(tweets), filename)
    header = ["id"]
    header.extend(Tweet.get_all_keys())
    with open(filename, 'wb') as testfile:
        csv_writer = csv.writer(testfile)
        csv_writer.writerow(header)
        for t in tweets:
            line = [t.get_id()]
            for key in Tweet.get_all_keys(): line.append(t[key])
            csv_writer.writerow(line)


def get_index_from_filename(filename):
    # type: (str) -> str
    for i in get_all_indices():
        if filename.startswith(i):
            return i
