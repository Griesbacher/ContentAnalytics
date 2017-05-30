import nltk
import string


class Normalizer:
    def __init__(self):
        self._st = nltk.stem.porter.PorterStemmer()
        self._wln = nltk.WordNetLemmatizer()
        nltk.download('punkt')

    def stem(self, text):
        return " ".join([self._st.stem(token) for token in self._tokenize(text)])

    def lem(self, text):
        result = list()
        for word in nltk.pos_tag(self._tokenize(text), tagset='universal'):
            try:
                result.append(self._wln.lemmatize(word[0], word[1][0].lower()))
            except:
                pass
        return " ".join(result)

    def _tokenize(self, text):
        return nltk.word_tokenize(text.lower().translate(None, string.punctuation))


if __name__ == '__main__':
    print Normalizer().stem("At eight o'clock on Thursday morning... Arthur didn't feel very good.")
    print Normalizer().lem("At eight o'clock on Thursday morning... Arthur didn't feel very good.")
