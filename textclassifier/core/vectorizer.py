import collections
from functools import reduce

import numpy as np

from textclassifier.core.preprocessing.text import TextToWordsConverter


class TfidfVectorizer(object):
    """ Convert a texts to TF-IDF features. """

    def __init__(self, to_words_converter=TextToWordsConverter()):
        self._idf = {}
        self._converter = to_words_converter

    @property
    def splitter(self):
        return self._splitter

    @splitter.setter
    def splitter(self, value):
        if not value:
            raise ValueError("The given splitter can't be none.")
        self._splitter = value

    @property
    def preprocessor(self):
        return self._preprocessor

    @preprocessor.setter
    def preprocessor(self, value):
        if not value:
            raise ValueError("The given preprocessor can't be none.")
        self._preprocessor = value

    def _get_texts_words(self, text):
        return self._converter.convert(text)

    def _count_idf(self, texts):
        id = 0
        for text in texts:
            for word in text:
                # if _idf already has this word
                if self._idf.get(word):
                    continue

                # calculate the number of documents which has this word
                count = reduce(lambda x, y: x + 1 if word in y else x, texts, 0)
                self._idf[word] = (id, np.log10(len(texts) / count))
                id += 1

    @staticmethod
    def _count_tf(text_words):
        count_words = collections.Counter(text_words)
        length = float(len(count_words))
        return {key: count_words[key] / length for key in count_words}

    def _transform(self, x, texts):
        """ Count TF-IDF for each text in the given list of texts. """
        if not self._idf:
            raise ValueError("Model is not trained.")

        res = np.zeros((len(x), len(self._idf)))

        if not texts:
            texts = [self._get_texts_words(text) for text in x]

        for i, text in enumerate(texts):
            tf = TfidfVectorizer._count_tf(text)
            for k, v in tf.items():
                if not self._idf.get(k):
                    continue
                idf = self._idf[k]
                res[i, idf[0]] = idf[1] * v

        return res

    def _train(self, x):
        texts = [self._get_texts_words(text) for text in x]
        self._count_idf(texts)
        return texts

    def train(self, x):
        self._train(x)

    def transform(self, x):
        return self._transform(x=x, texts=None)

    def train_transform(self, x):
        texts = self._train(x)
        return self._transform(x=x, texts=texts)
