import re
import nltk

STOPWORDS = set(nltk.corpus.stopwords.words('english'))

# Custom stopwords
STOPWORDS.update({
    '–',
    'yoon',
    'country',
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
    'need', 'say', 'fill', 'week', 'think', 'go', 'job', 'total', 'motion', 'threshold',
    'sitting', 'seat', 'fist', 'member'
})

# PoS Tag Classifications
ADJECTIVES = ['JJ', 'JJR', 'JJS']
NOUNS = ['NN', 'NNS']
PROPER_NOUNS = ['NNP', 'NNPS']
VERBS = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

# Multi-word tokens
MULTI_WORD_TOKENS = [
    ('South', 'Korea'),
    ('Constitutional', 'Court'),
    ('Democratic', 'party'),
    ('People', 'Power', 'Party'),
    ('acting', 'president'),
    ('prime', 'minister'),
    ('ruling', 'party'),
    ('martial', 'law'),
    ('Corruption', 'Investigation', 'Office', 'for', 'High-Ranking', 'Officials')
]

# Set of proper nouns that need to be included in analysis.
# If a proper noun is not contained in following list,
# it'll be excluded by the function `arrange_tokens`.
INCLUDED_PROPER_NOUNS = [
    'constitutional court',
    'national assembly',
    'corruption investigation office for high-ranking officials'
    'cio'
]

wlem = nltk.WordNetLemmatizer()
mwe_tk = nltk.tokenize.MWETokenizer(MULTI_WORD_TOKENS, separator=' ')

def get_sentences(text):
    for row in text.split('\n'):
        for sent in re.split(r'[\.\?\!]\s+', row):
            yield sent

def lower_first_character(sentence):
    b = list(sentence)
    b[0] = sentence[0].lower()
    return ''.join(b)

def replace_stylized_punctuations(text):
    sub1 = re.sub(r'[“”]', '"', text)
    sub2 = re.sub(r'[‘’]', "'", sub1)
    return sub2

def remove_apostrophe(sentence):
    return re.sub(r"(\S)[']s", r'\1', sentence)

def remove_abbreviations(sentence):
    return re.sub(r'\([A-Z]+\)', '', sentence)

def arrange_tokens(tagged_tokens):
    result = []
    i = 0
    while i < len(tagged_tokens):
        token, tag = tagged_tokens[i]
        candidate = None
        if tag in PROPER_NOUNS:
            NNP_tokens = [token]
            j = i + 1
            while j < len(tagged_tokens) and tagged_tokens[j][1] == tag:
                NNP_tokens.append(tagged_tokens[j][0])
                j += 1
            full_word = ' '.join(NNP_tokens)
            if full_word.lower() in INCLUDED_PROPER_NOUNS:
                candidate = (full_word, 'PN')
            i = j - 1
        elif tag in NOUNS:
            candidate = (wlem.lemmatize(token.lower(), 'n'), 'N')
        elif tag in VERBS:
            candidate = (wlem.lemmatize(token.lower(), 'v'), 'V')
        elif tag in ADJECTIVES:
            candidate = (wlem.lemmatize(token.lower(), 'a'), 'A')
        if candidate is not None and candidate[0] not in STOPWORDS:
            result.append(candidate)
        i += 1
    return result

def preprocess_sentence(sentence):
    sentence = sentence.strip()
    if sentence == "":
        return None
    sentence = replace_stylized_punctuations(sentence)
    sentence = remove_abbreviations(sentence)
    sentence = remove_apostrophe(sentence)
    tokens = nltk.word_tokenize(sentence)
    tokens = mwe_tk.tokenize(tokens)
    tagged = nltk.pos_tag(tokens)
    print(' '.join([tag for _, tag in tagged]))
    arranged = arrange_tokens(tagged)
    return arranged

def preprocess(text):
    # cleaned_text = re.sub(r'[^\w\d\s]', '', text)
    data = []
    for sentence in get_sentences(text):
        result = preprocess_sentence(sentence)
        if result is not None:
            data.append(result)
    return data
