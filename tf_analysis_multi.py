import os
import statistics
from core import Article
from wordcloud import WordCloud
import matplotlib.pyplot as plt

DATA_PATH = 'data'
OUTPUT_PATH = 'output'
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
    print(f'\n========== Analyzing {basename} ==========')
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
            token_scores[article_id][token] = -10
        elif standard_deviations[token] == 0:
            token_scores[article_id][token] = 0
        else:
            stdscore = (counts[token].get(article_id, 0) - average) / standard_deviations[token] * 100
            token_scores[article_id][token] = stdscore

word_scores = {}
sentence_scores = {}

for article_id in token_scores.keys():
    sentence_evaluations = []
    for i, sentence in enumerate(articles[article_id].sentences):
        sentence_evaluations.append((
            i, sentence,
            sum(token_scores[article_id].get(token, 0) for token, _ in sentence.tokens)
        ))
    sentence_scores[article_id] = sorted(sentence_evaluations, key=lambda x: x[2], reverse=True)
    word_scores[article_id] = sorted(token_scores[article_id].items(), key=lambda x: x[1], reverse=True)

print('\n===============================================')
print(f'Writing outputs in directory {OUTPUT_PATH}...')

if not os.path.exists(OUTPUT_PATH):
    os.mkdir(OUTPUT_PATH)
elif not os.path.isdir(OUTPUT_PATH):
    print(f'Error: {OUTPUT_PATH} is not a directory.')
    import sys
    sys.exit()

for article_id in articles.keys():
    print(f' - Saving analysis report of article {article_id}...', end=' ')
    f = open(os.path.join(OUTPUT_PATH, f'Report_{article_id}.txt'), 'w')
    f.write(f'========== Top 10 sentences of `{article_id}` ==========\n')
    for i, (_, sentence, score) in enumerate(sentence_scores[article_id][:10], start=1):
        f.write(f'{i}. ')
        f.write(sentence.original_sentence)
        f.write(f' ({score:.4f})\n')
    f.write(f'\n========== Top 10 words of `{article_id}` ==========\n')
    for i, (word, score) in enumerate(word_scores[article_id][:10], start=1):
        f.write(f'\n{i}. {word} ({score:.4f})\n')
        for j, (_, sentence) in enumerate(articles[article_id].find(word), start=1):
            f.write(f'  {j}) {sentence.original_sentence}\n')
    f.close()
    print('done.')

print(f'Successfully wrote reports in directory {OUTPUT_PATH}.')

# dict_for_wordcloud = {k:int(s) for k, s in word_scores[KEY]}
wordcloud = WordCloud(
    background_color='white',
    width=1500, height=800,
    max_font_size=70,
    colormap='tab10',
    collocations=False
)
# wordcloud.generate_from_frequencies(dict_for_wordcloud)
wordcloud.generate_from_frequencies(frequencies=entire_count)
plt.figure()
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()
