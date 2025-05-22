from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import euclidean_distances
from scipy.sparse.csgraph import minimum_spanning_tree
import numpy as np
import networkx as nx
import pickle

WORD2VEC_PATH = "./models/word2vec.model"

def get_entities_list(word2vec, functional_triplets):
    words = []

    for triplet in functional_triplets:
        w1 = triplet[0].split(' ')[0]
        w2 = triplet[2].split(' ')[0]

        if w1 in word2vec.wv.key_to_index:
            words.append(w1)
        if w2 in word2vec.wv.key_to_index:
            words.append(w2)

    words = list(set(words))

    return words

def cluster_entities(entity_embeddings, n_clusters=50):

    pca = PCA(n_components=20)
    reduced_vectors = pca.fit_transform(entity_embeddings)

    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(reduced_vectors)

    labels = kmeans.labels_

    print("clusters done")

    return labels

def build_mst(entity_embeddings, entity_names):

    distance_matrix = euclidean_distances(entity_embeddings)

    mst = minimum_spanning_tree(distance_matrix)

    mst_edges = np.array(mst.nonzero()).T
    edge_weights = mst[mst.nonzero()].A1

    mst_graph = []
    for (i, j), weight in zip(mst_edges, edge_weights):
        mst_graph.append((entity_names[i], entity_names[j], weight))

    return mst_graph

def extract_triplets_from_mst(entity_embeddings, entity_names):
    mst_graph = build_mst(entity_embeddings, entity_names)


    G = nx.Graph()
    for src, tgt, weight in mst_graph:
        G.add_edge(src, tgt, weight=weight)

    # Выбор корня (центр MST)
    root = min(entity_names, key=lambda x: np.mean(list(nx.single_source_dijkstra_path_length(G, x).values())))

    # DFS для извлечения иерархии
    visited = set()
    triplets = []

    def dfs(node, parent=None):
        visited.add(node)
        if parent:
            triplets.append([parent, "has_child", node])
        for neighbor in G.neighbors(node):
            if neighbor not in visited:
                dfs(neighbor, node)

    dfs(root)
    return triplets


def extract_hierarchical_relations(word2vec, functional_triplets):

    hierarchy_triplets = []

    words = get_entities_list(word2vec, functional_triplets)
    vectors = [word2vec.wv[w] for w in words]

    num_clusters = 50
    labels = cluster_entities(vectors)

    for cluster_id in range(num_clusters):
        cluster_words = [word for word, label in zip(words, labels) if label == cluster_id]
        cluster_vectors = []
        for w in cluster_words:
            vector = word2vec.wv[w]
            cluster_vectors.append(vector)

        if 1 < len(cluster_words) < 15:
            hierarchy_cluster_triplets = extract_triplets_from_mst(cluster_vectors, cluster_words)
            hierarchy_triplets += hierarchy_cluster_triplets

    return hierarchy_triplets


if __name__ == "__main__":


    with open('triplets', 'rb') as f:
        triplets = pickle.load(f)
        print(triplets)

    model = Word2Vec.load(WORD2VEC_PATH)

    hi_triplets = extract_hierarchical_relations(model, triplets)
    print(hi_triplets)