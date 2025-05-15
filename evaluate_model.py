from gensim.models import Word2Vec
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import random

def sparsity_test(model):
    all_vectors = np.array([model.wv[word] for word in model.wv.key_to_index])

    # Гистограмма значений
    plt.figure(figsize=(10, 6))
    plt.hist(all_vectors.flatten(), bins=100, alpha=0.7, color='blue')
    plt.title("Распределение значений компонент векторов")
    plt.xlabel("Значение компоненты")
    plt.ylabel("Частота")
    plt.grid(True)
    zero_count = np.sum(all_vectors.flatten() == 0)
    total_count = all_vectors.size
    plt.annotate(
        f"Нулевые элементы: {zero_count}/{total_count} ({zero_count / total_count:.4%})",
        xy=(0, 0),
        xytext=(0.5, 0.95),
        textcoords='axes fraction',
        ha='center',
        bbox=dict(boxstyle='round', fc='white', alpha=0.8)
    )
    plt.show()

def plot_words_heat_map(words, model, title):
    similarity_matrix = np.zeros((len(words), len(words)))

    for i, word1 in enumerate(words):
        for j, word2 in enumerate(words):
            similarity_matrix[i][j] = model.wv.similarity(word1, word2)

    # 4. Построение тепловой карты
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        similarity_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        xticklabels=words,
        yticklabels=words,
        linewidths=0.5,
        cbar_kws={'label': 'Косинусное сходство'}
    )

    plt.title(title, pad=20, fontsize=16)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.show()


model = Word2Vec.load('./models/word2vec.model')
print(model.wv.most_similar("водород", topn=10))
print(model.wv.most_similar("электролиз", topn=10))
print(model.wv.most_similar("реакция", topn=10))
print(model.wv.most_similar("рис", topn=10))



all_words = list(model.wv.key_to_index.keys())
words = ["водород", "автор", "пламя", "топливо", "материал", "вещество", "гидрид", "электрод", "нагревать", "статья"]

plot_words_heat_map(words, model, "Тепловая карта косинусного сходства между словами (skip-gram)")
sparsity_test(model)