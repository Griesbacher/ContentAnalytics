import pprint


class Tweet(dict):
    _all_keys = None
    _all_unknown_keys = None

    def __init__(self, *args, **kwargs):
        super(Tweet, self).__init__(*args, **kwargs)
        if len(self) == 0:
            for k in Tweet.get_all_keys():
                self[k] = 0.0
            self["id"] = -1
            self["tweet"] = ""

    def get_tweet(self):
        return self["tweet"]

    def set_tweet(self, tweet):
        self["tweet"] = tweet
        return self

    def get_id(self):
        return self["id"]

    def set_id(self, new_id):
        self["id"] = new_id
        return self

    def normalize(self):
        def norm(get_keys_func):
            values = []
            for k in get_keys_func():
                if k in self:
                    values.append(self[k])
                else:
                    values.append(0)

            overall_sum = sum(values)
            if overall_sum == 0:
                return values
            factor = 1.0 / overall_sum
            for v in range(len(values)):
                values[v] *= factor
            return values

        s_values = norm(Tweet.get_s_keys)
        for i in range(len(Tweet.get_s_keys())):
            self[Tweet.get_s_keys()[i]] = s_values[i]

        w_values = norm(Tweet.get_w_keys)
        for i in range(len(Tweet.get_w_keys())):
            self[Tweet.get_w_keys()[i]] = w_values[i]
        return self

    @staticmethod
    def get_k_keys():
        return ["k1", "k2", "k3", "k4", "k5", "k6", "k7", "k8", "k9", "k10", "k11", "k12", "k13", "k14", "k15"]

    @staticmethod
    def get_s_keys():
        return ["s1", "s2", "s3", "s4", "s5"]

    @staticmethod
    def get_w_keys():
        return ["w1", "w2", "w3", "w4"]

    @staticmethod
    def get_all_keys():
        if Tweet._all_keys is None:
            Tweet._all_keys = []
            Tweet._all_keys.extend(Tweet.get_s_keys())
            Tweet._all_keys.extend(Tweet.get_w_keys())
            Tweet._all_keys.extend(Tweet.get_k_keys())
        return Tweet._all_keys

    @staticmethod
    def get_unknown_k_key():
        return "k7"

    @staticmethod
    def get_unknown_s_key():
        return "s1"

    @staticmethod
    def get_unknown_w_key():
        return "w3"

    @staticmethod
    def get_all_unknown_keys():
        if Tweet._all_unknown_keys is None:
            Tweet._all_unknown_keys = [Tweet.get_unknown_k_key(), Tweet.get_unknown_s_key(), Tweet.get_unknown_w_key()]
        return Tweet._all_unknown_keys

    def __str__(self):
        return pprint.pformat(self).__str__()
