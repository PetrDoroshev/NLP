import numpy as np
import matplotlib.pyplot as plt
from gensim.models import Word2Vec
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import dendrogram
import matplotlib.cm as cm

def plot_dendrogram(model, **kwargs):
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)


model = Word2Vec.load('word2vec.model')

vectors = [model.wv[w] for w in model.wv.key_to_index]
words = [w for w in model.wv.key_to_index]
distance_matrix = squareform(pdist(vectors, metric='cosine'))

clustering = AgglomerativeClustering(
    n_clusters=None,
    affinity='precomputed',
    linkage='complete',
    distance_threshold=0.25
)

labels = clustering.fit_predict(distance_matrix)


"""plt.title("Hierarchical Clustering Dendrogram")
# plot the top three levels of the dendrogram
plot_dendrogram(model, truncate_mode="level", p=3)
plt.xlabel("Number of points in node (or index of point if no parenthesis).")
plt.show()"""


clusters = {}
n = 0
for item in labels:

    if item in clusters:
        clusters[item].append(words[n])
    else:
        clusters[item] = [words[n]]
    n += 1

for item in clusters:
    print ("Cluster ", item, "-", len(clusters[item]))
    for i in clusters[item]:
        print(i)