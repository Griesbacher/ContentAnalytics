import pprint


class Tweet(dict):
    def __init__(self, *args, **kwargs):
        super(Tweet, self).__init__(*args, **kwargs)

    @staticmethod
    def get_k_keys():
        return ["k1", "k2", "k3", "k4", "k5", "k6", "k7", "k8", "k9", "k10", "k11", "k12", "k13", "k14", "k15"]

    @staticmethod
    def get_s_keys():
        return ["s1", "s2", "s3", "s4", "s5"]

    @staticmethod
    def get_w_keys():
        return ["w1", "w2", "w3", "w4"]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return pprint.pformat(self).__str__()
