import os
import statistics
from core import Article
from wordcloud import WordCloud
import matplotlib.pyplot as plt

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

entire_count = {}

for filepath in FILES:
    basename = os.path.basename(filepath)
    article_id = os.path.splitext(basename)[0]
    print(f'========== Analyzing {basename} ==========')
    with open(filepath, 'r') as f:
        text = f.read()
    articles[article_id] = Article(article_id, text)

for article_id, article in articles.items():
    for sentence in article.sentences:
        for token, tag in sentence.tokens:
            if tag in TOKEN_COUNT_CRITERIA:
                if token not in counts:
                    counts[token] = {i: 0 for i in articles.keys()}
                counts[token][article_id] = counts[token].get(article_id, 0) + 1
                entire_count[token] = entire_count.get(token, 0) + 1

average_usages = {}
standard_deviations = {}

for token in counts:
    values = list(counts[token].values())
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
            token_scores[article_id][token] = 50
        elif standard_deviations[token] == 0:
            token_scores[article_id][token] = 0
        else:
            stdscore = (counts[token].get(article_id, 0) - average) / standard_deviations[token] * 100
            token_scores[article_id][token] = stdscore

word_scores = {}

top10_sentences = {}

for article_id in token_scores.keys():
    sentence_scores = []
    for i, sentence in enumerate(articles[article_id].sentences):
        sentence_scores.append((i, sum(token_scores[article_id].get(token, 0) for token, _ in sentence.tokens)))
    sentence_scores.sort(key=lambda x: x[1], reverse=True)
    top10_sentences[article_id] = [articles[article_id].sentences[i] for i, _ in sentence_scores[:10]]
    word_scores[article_id] = sorted(token_scores[article_id].items(), key=lambda x: x[1], reverse=True)

# dict_for_wordcloud = {k:int(s) for k, s in word_scores[KEY]}
wordcloud = WordCloud(
    background_color='white',
    width=1000, height=500,
    max_font_size=60,
    colormap='tab10',
    collocations=False
)
# wordcloud.generate_from_frequencies(dict_for_wordcloud)
wordcloud.generate_from_frequencies(frequencies=entire_count)
plt.figure()
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()
