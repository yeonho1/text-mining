from preprocessor import get_sentences
from preprocessor import preprocess_sentence

class Sentence:
    _original_sentence = ""
    _tokens = []

    def __init__(self, original_text):
        self._original_sentence = original_text
        self._tokens = preprocess_sentence(original_text)

    def __repr__(self):
        return f'<Sentence: "{self._original_sentence}">'

    @property
    def original_sentence(self):
        return self._original_sentence

    @property
    def tokens(self):
        return self._tokens

class Article:
    _id = ""
    _original_text = ""
    _sentences = []

    def __init__(self, id, original_text):
        self._id = id
        self._original_text = original_text
        self._sentences = []
        for sentence in get_sentences(original_text):
            self._sentences.append(Sentence(sentence))

    def __repr__(self):
        return f'<Article `{self._id}`>'

    @property
    def id(self):
        return self._id

    @property
    def original_text(self):
        return self._original_text

    @property
    def sentences(self):
        return self._sentences

    def find(self, token_to_find):
        result = []
        for i, sentence in enumerate(self._sentences, start=1):
            if any([token == token_to_find for token, tag in sentence.tokens]):
                result.append((i, sentence))
        return result
