import os
import statistics
from core import Article

DATA_PATH = 'data'
TOKEN_COUNT_CRITERIA = [
    'N', 'PN',
    # 'V',
    # 'A'
]

FILES = []

print('Collecting files to analyze...', end=' ')

for path, dirs, files in os.walk(DATA_PATH):
    FILES.extend([os.path.join(path, file) for file in files])

print(f'found {len(FILES)} files.')

articles = {}
counts = {}

for filepath in FILES:
    basename = os.path.basename(filepath)
    article_id = os.path.splitext(basename)[0]
    print(f'========== Analyzing {basename} ==========')
    with open(filepath, 'r') as f:
        text = f.read()
    articles[article_id] = Article(article_id, text)
    for sentence in articles[article_id].sentences:
        for token, tag in sentence.tokens:
            if tag in TOKEN_COUNT_CRITERIA:
                if token not in counts:
                    counts[token] = {}
                counts[token][article_id] = counts[token].get(article_id, 0) + 1

average_usages = {}
standard_deviations = {}

for token in counts:
    values = list(counts[token].values())
    if len(values) < len(FILES):
        values.extend([0] * (len(FILES) - len(values)))
    average_usages[token] = statistics.mean(values)
    standard_deviations[token] = statistics.stdev(values)

# average_ranking = [(k, i) for k, i in average_usages.items() if i >= 1]
# average_ranking.sort(key=lambda x: x[1], reverse=True)
stdev_list = [(k, standard_deviations[k]) for k, i in average_usages.items()]

token_scores = {}

for article_id in articles:
    token_scores[article_id] = {}
    for token, average in average_usages.items():
        if average < 1:
            continue
        if standard_deviations[token] == 0:
            token_scores[article_id][token] = 0
        else:
            stdscore = (counts[token].get(article_id, 0) - average) / standard_deviations[token] * 100
            token_scores[article_id][token] = stdscore

top10_words = {}

top10_sentences = {}

for article_id in token_scores:
    sentence_scores = []
    for i, sentence in enumerate(articles[article_id].sentences):
        sentence_scores.append((i, sum(token_scores[article_id].get(token, 0) for token, _ in sentence.tokens)))
    sentence_scores.sort(key=lambda x: x[1], reverse=True)
    top10_sentences[article_id] = [articles[article_id].sentences[i] for i, _ in sentence_scores[:10]]
    top10_words[article_id] = sorted(token_scores[article_id].items(), key=lambda x: x[1], reverse=True)[:10]

print('\n\n')

KEY = 'CNN-south-korea-impeachment-vote-acting-president-intl-hnk'

print(f'===== Top 10 sentences of article `{KEY}` =====')

for i, sentence in enumerate(top10_sentences[KEY], start=1):
    print(f'{i}. {sentence.original_sentence}')

print('\n')
print(f'===== Top 10 words of article `{KEY}` =====')
# print(top5_words[KEY])
for i, (word, s) in enumerate(top10_words[KEY], start=1):
    print(f'{i}. {word} ({s})')

# print(average_ranking)
# print(stdev_list)
# print(scores)
