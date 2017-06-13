import traceback

try:
    import enchant

    enchant_enabled = True
except Exception:
    enchant_enabled = False
import re
import sys
import nltk
import string


# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')


class Normalizer:
    _st = nltk.stem.porter.PorterStemmer()
    _wln = nltk.WordNetLemmatizer()
    if enchant_enabled:
        _spell_dict = enchant.Dict("en_US")
    _max_dist = 3
    __regex_search = r'(\w)\1{2,}'
    __regex_replace_single = r'\1'
    __regex_replace_double = r'\1\1'
    _allowed_word_types = [
        nltk.corpus.reader.wordnet.ADJ,
        nltk.corpus.reader.wordnet.ADJ_SAT,
        nltk.corpus.reader.wordnet.ADV,
        nltk.corpus.reader.wordnet.NOUN,
        nltk.corpus.reader.wordnet.VERB
    ]
    _printable = set(string.printable)

    @staticmethod
    def stem(text):
        return " ".join([Normalizer._st.stem(token) for token in Normalizer.tokenize(text)])

    @staticmethod
    def lem(text, use_autocorrect=False):
        try:
            result = ""
            tokens = Normalizer.tokenize(text)
            if use_autocorrect:
                tokens = [Normalizer.autocorrect_word(t) for t in tokens]
            for word in nltk.pos_tag(tokens, tagset='universal'):
                if word[1][0].lower() in Normalizer._allowed_word_types:
                    try:
                        result += Normalizer._wln.lemmatize(word[0], word[1][0].lower()) + " "
                    except UnicodeDecodeError:
                        pass
                else:
                    result += word[0]
            return result
        except:
            traceback.print_exc()
            return text

    @staticmethod
    def tokenize(text):
        return nltk.word_tokenize(filter(lambda x: 32 <= ord(x) <= 126, text.translate(None, string.punctuation)))

    @staticmethod
    def init(dict_name, max_dist):
        if enchant_enabled:
            Normalizer._spell_dict = enchant.Dict(dict_name)
        Normalizer._max_dist = max_dist

    @staticmethod
    def _dictionary_lookup(word):
        if enchant_enabled:
            for s in Normalizer._spell_dict.suggest(word):
                d = nltk.edit_distance(word, s)
                if d < Normalizer._max_dist:
                    return s, d

        return word, sys.maxint

    @staticmethod
    def _shrink_multiple_chars_to_one(word):
        return re.sub(Normalizer.__regex_search, Normalizer.__regex_replace_single, word)

    @staticmethod
    def _shrink_multiple_chars_to_two(word):
        return re.sub(Normalizer.__regex_search, Normalizer.__regex_replace_double, word)

    @staticmethod
    def is_valid_word(word):
        if enchant_enabled:
            return Normalizer._spell_dict.check(word)
        else:
            return False

    @staticmethod
    def autocorrect_sentence(sentence):
        result = list()
        for word in Normalizer.tokenize(sentence):
            result.append(Normalizer.autocorrect_word(word))
        return " ".join(result)

    @staticmethod
    def autocorrect_word(word):
        if len(word) < 2:
            return word

        if Normalizer.is_valid_word(word): return word
        word_doubles = Normalizer._shrink_multiple_chars_to_two(word)
        if Normalizer.is_valid_word(word_doubles): return word_doubles
        word_singles = Normalizer._shrink_multiple_chars_to_one(word)
        if Normalizer.is_valid_word(word_singles): return word_singles

        suggestion_double, value_double = Normalizer._dictionary_lookup(word_doubles)
        suggestion_single, value_single = Normalizer._dictionary_lookup(word_singles)
        if value_single < value_double:
            return suggestion_single
        elif value_double < value_single:
            return suggestion_double
        else:
            return suggestion_double


if __name__ == '__main__':
    print Normalizer().stem("At eight o'clock on Thursday morning... Arthur didn't feel very good.")
    print Normalizer().lem("At eight o'clock on Thursday morning... Arthur didn't feel very good.")
    print Normalizer.autocorrect_word("hoooottttt")
    print Normalizer.autocorrect_word("glllooooorious")
    print Normalizer.autocorrect_word("moon")
    print Normalizer.autocorrect_word("mooon")
    print Normalizer.autocorrect_word("mooone")
    print Normalizer.autocorrect_sentence("hoooottttt glllooooorious moooney!!!!!")
    print Normalizer.autocorrect_sentence("hoooottttt glllooooorious moooney!!!!!")

    print Normalizer().lem("hello did hoooottttt glllooooorious moooney!!!!!")
    print Normalizer().lem("hello did hoooottttt glllooooorious moooney!!!!!", True)
