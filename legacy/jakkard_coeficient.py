import os
import pymupdf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer


def jaccard_similarity(text1, text2):
    """Вычисляет коэффициент Жаккара между двумя текстами"""
    vectorizer = CountVectorizer(binary=True).fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    intersection = np.sum(vectors[0] & vectors[1])
    union = np.sum(vectors[0] | vectors[1])
    return intersection / union if union != 0 else 0


def plot_jaccard_heatmap(texts, titles=None, figsize=(12, 10)):
    """
    Строит тепловую карту коэффициентов Жаккара между текстами

    :param texts: Список текстов для сравнения
    :param titles: Подписи для текстов (если None, используются индексы)
    :param figsize: Размер графика
    """
    if titles is None:
        titles = [f"Текст {i + 1}" for i in range(len(texts))]

    # Создаем матрицу попарных коэффициентов Жаккара
    n = len(texts)
    jaccard_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            jaccard_matrix[i][j] = jaccard_similarity(texts[i], texts[j])

    # Преобразуем в DataFrame для удобства
    df = pd.DataFrame(jaccard_matrix, index=titles, columns=titles)

    # Строим тепловую карту
    plt.figure(figsize=figsize)
    sns.heatmap(
        df,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=0,
        vmax=1,
        linewidths=0.5,
        cbar_kws={'label': 'Коэффициент Жаккара'},
        annot_kws={"fontsize": 8}

    )
    plt.title("Тепловая карта схожести текстов (коэффициент Жаккара)", pad=20)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig("heat_map_4.png")
    plt.show()

if __name__ == "__main__":

    texts = []
    titles = []

    for filename in sorted(os.listdir("./txt_articles")):

        with open(f'./txt_articles/{filename}', 'r', encoding="utf-8") as file:
            text = file.read().replace('\n', '')
            texts.append(text)
            titles.append(filename.split(".")[0])


    plot_jaccard_heatmap(texts, titles)