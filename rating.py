import nltk
from normalizer import Normalizer
from nltk.corpus import wordnet


class Rater:
    _future_keywords = set([item for sublist in
                            [word.lemma_names() for word in wordnet.synsets("tomorrow")]
                            + [word.lemma_names() for word in wordnet.synsets("future")]
                            for item in sublist])
    _present_keywords = set([item for sublist in
                             [word.lemma_names() for word in wordnet.synsets("today")]
                             for item in sublist])
    _past_keywords = set([item for sublist in
                          [word.lemma_names() for word in wordnet.synsets("yesterday")]
                          + [word.lemma_names() for word in wordnet.synsets("past")]
                          for item in sublist])

    @staticmethod
    def determine_tense_input(text):
        tokens = Normalizer.tokenize(text)
        tagged = nltk.pos_tag(tokens)

        tense = {
            "future": 0,
            "present": 0,
            "past": 0,
        }
        for word in tagged:
            if word[1] == "MD" or word[0] in Rater._future_keywords:
                tense["future"] += 1
            elif word[1] in ["VBP", "VBZ", "VBG"] or word[0] in Rater._present_keywords:
                tense["present"] += 1
            elif word[1] in ["VBD", "VBN"] or word[0] in Rater._past_keywords:
                tense["past"] += 1
        return tense

    @staticmethod
    def post_tense(tweet):
        tense = Rater.determine_tense_input(tweet.get_tweet())
        tweet["w1"] *= (tense["present"] / 2 + 1)
        tweet["w2"] *= (tense["future"] / 2 + 1)
        tweet["w4"] *= (tense["past"] / 2 + 1)
        if tense["present"] == 0 and tense["future"] == 0 and tense["past"] == 0:
            tweet["w4"] = 1
        return tweet


if __name__ == '__main__':
    # future
    print Rater.determine_tense_input(
        "With the snow forecast for Tahoe this weekend, maybe the @mention riders need to bust out the 'Cross bikes :) @mention")
    print Rater.determine_tense_input(
        "...CRITICAL FIRE WEATHER CONDITIONS EXPECTED FRIDAY AFTERNOON... .RED FLAG WARNING CONDITIONS ARE POSSIBLE THIS AFTERNO {link}")

    # present
    print Rater.determine_tense_input(
        "Father. Son. Holy ghost. Amen... hope I come out alive =) (this is the Hot~ness) Namaste*!~ {link}")
    print Rater.determine_tense_input(
        "Can already tell it's going to be a tough scoring day. It's as windy right now as it was yesterday afternoon.")
    # past
    print Rater.determine_tense_input(
        "It was 102 degrees yesterday. I am not ready for this heat. San Diego sounds good right about now")
    print Rater.determine_tense_input(
        "Currently working on Melissa and Josh's engagement photos from this past rainy weekend. Can't wait to share.")
