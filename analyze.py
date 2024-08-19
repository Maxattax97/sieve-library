#!/usr/bin/env python3

from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import silhouette_score
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import psycopg2

# PostgreSQL connection details
db_config = {
    "dbname": "sieve",
    "user": "sieve",
    "password": "Fate9chap9priest",
    "host": "localhost",
    "port": "5432",
}


def load_data_from_db():
    """Load word occurrences data from the PostgreSQL database."""
    conn = psycopg2.connect(**db_config)
    query = """
        SELECT
            e.id AS email_id,
            w.word,
            o.count
        FROM
            subject_occurrences o
        JOIN
            words w ON o.word_id = w.id
        JOIN
            emails e ON o.email_id = e.id;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# Elbow Method to determine optimal number of clusters
def elbow_analysis(X):
    wcss = []
    for i in range(2, 15):
        kmeans = KMeans(
            n_clusters=i, init="k-means++", max_iter=300, n_init=10, random_state=42
        )
        kmeans.fit(X)
        wcss.append(kmeans.inertia_)
    plt.plot(range(2, 15), wcss)
    plt.title("Elbow Analysis")
    plt.xlabel("Number of clusters")
    plt.ylabel("WCSS")
    plt.show()


# Silhouette Score to evaluate clustering performance
def silhouette_analysis(X):
    silhouette_scores = []
    for i in range(2, 15):
        kmeans = KMeans(n_clusters=i, random_state=42)
        kmeans.fit(X)
        score = silhouette_score(X, kmeans.labels_)
        silhouette_scores.append(score)

    plt.plot(range(2, 15), silhouette_scores)
    plt.title("Silhouette Score Analysis")
    plt.xlabel("Number of clusters")
    plt.ylabel("Silhouette Score")
    plt.show()


def plot_3d_pca(dtm, cluster_col="cluster", n_components=3, tfidf=True, cmap="viridis"):
    """
    Plots a 3D PCA scatter plot of the document-term matrix (DTM).

    Parameters:
    - dtm: pd.DataFrame
        Document-term matrix with a cluster column.
    - cluster_col: str
        The name of the column containing cluster labels.
    - n_components: int
        Number of PCA components to reduce to (default is 3).
    - tfidf: bool
        Whether to apply TF-IDF transformation before PCA (default is True).
    - cmap: str
        Colormap for the scatter plot (default is 'viridis').

    Returns:
    - None
    """
    # Separate the cluster labels
    clusters = dtm[cluster_col]
    dtm_no_cluster = dtm.drop(columns=[cluster_col])

    # Apply TF-IDF transformation if specified
    if tfidf:
        tfidf_transformer = TfidfTransformer(norm=None, use_idf=True, smooth_idf=True)
        dtm_transformed = tfidf_transformer.fit_transform(dtm_no_cluster)
    else:
        dtm_transformed = dtm_no_cluster

    # Perform PCA to reduce the dimensionality
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(dtm_transformed.toarray())

    # Convert the PCA result to a DataFrame for easier plotting
    pca_df = pd.DataFrame(pca_result, columns=[f"PC{i+1}" for i in range(n_components)])
    pca_df[cluster_col] = clusters.values

    # Plot the 3D PCA plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    # Scatter plot, color-coded by cluster
    scatter = ax.scatter(
        pca_df["PC1"],
        pca_df["PC2"],
        pca_df["PC3"],
        c=pca_df[cluster_col],
        cmap=cmap,
        marker="o",
    )

    # Set labels
    ax.set_xlabel("Principal Component 1")
    ax.set_ylabel("Principal Component 2")
    ax.set_zlabel("Principal Component 3")
    ax.set_title("3D PCA of Email Data")

    # Add a color bar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Cluster")

    plt.show()


data = load_data_from_db()
print(data.head())

# Pivot the data to create a document-term matrix (DTM)
dtm = data.pivot_table(index="email_id", columns="word", values="count", fill_value=0)
print(dtm.head())

# elbow_analysis(dtm)  # definitely 6
# silhouette_analysis(dtm)  # definitely 4, maybe 13
# exit(0)

# Number of clusters
n_clusters = 6

# Apply KMeans
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
labels = kmeans.fit_predict(dtm)

# Add the cluster labels to the original dataframe
dtm["cluster"] = labels

plot_3d_pca(dtm, cluster_col="cluster", n_components=3, tfidf=True, cmap="viridis")

# Calculate word frequencies per cluster
word_freq_per_cluster = dtm.groupby("cluster").sum()

# Normalize by cluster size
cluster_sizes = dtm["cluster"].value_counts().sort_index()
word_freq_per_cluster_normalized = word_freq_per_cluster.div(cluster_sizes, axis=0)

# Calculate a "characteristic score" using TF-IDF
tfidf_transformer = TfidfTransformer(norm=None, use_idf=True, smooth_idf=True)
tfidf_matrix = tfidf_transformer.fit_transform(word_freq_per_cluster_normalized)

# Convert TF-IDF matrix back to a DataFrame for easier analysis
tfidf_df = pd.DataFrame(
    tfidf_matrix.toarray(),
    index=word_freq_per_cluster.index,
    columns=word_freq_per_cluster.columns,
)

tfidf_df = tfidf_df.sub(tfidf_df.mean(axis=0), axis=1)

# Generate WordClouds for each cluster based on the characteristic words
for cluster_num in range(tfidf_df.shape[0]):
    # Get the TF-IDF scores for the cluster
    characteristic_words = tfidf_df.iloc[cluster_num].sort_values(ascending=False)
    print(f"Cluster {cluster_num}:")
    # print top 10
    for word, score in characteristic_words.head(10).items():
        print(f"  {word}: {score:.4f}")
    print("\n")

    # Generate the word cloud
    # wordcloud = WordCloud(
    # width=800, height=400, background_color="white"
    # ).generate_from_frequencies(characteristic_words)

    # Display the word cloud
    # plt.figure(figsize=(10, 5))
    # plt.imshow(wordcloud, interpolation="bilinear")
    # plt.title(f"WordCloud for Cluster {cluster_num}")
    # plt.axis("off")
    # plt.show()
