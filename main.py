#!/usr/bin/env python3

import os
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA, LatentDirichletAllocation
from sklearn.metrics import silhouette_score
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from collections import Counter
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from wordcloud import WordCloud

# Download NLTK data files (stopwords, etc.)
import nltk

nltk.download("punkt")
nltk.download("stopwords")


# Load emails from directory
def load_emails(directory):
    emails = []
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), "r", encoding="latin1") as file:
            emails.append(file.read())
    return emails


# Preprocess email text
# Preprocess email text with additional word filtering
def preprocess_email(text, filter_words=None):
    if filter_words is None:
        filter_words = []

    # Remove non-alphanumeric characters
    text = re.sub(r"[^a-zA-Z]+", " ", text)

    # Convert to lowercase
    text = text.lower()

    # Tokenize
    words = word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    words = [word for word in words if word not in stop_words]
    words = [
        word
        for word in words
        if word not in stop_words and word not in filter_words and len(word) > 4
    ]

    # Stemming
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]

    result = " ".join(words)
    # print(result)
    return result


# Generate and display a word cloud
def generate_wordcloud(text, cluster_num):
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
        text
    )
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.title(f"Word Cloud for Cluster {cluster_num}")
    plt.axis("off")
    plt.show()


# Get the top words in each cluster
def get_top_words(text, num_words=10):
    words = text.split()
    counter = Counter(words)
    common_words = counter.most_common(num_words)
    return common_words


# Elbow Method to determine optimal number of clusters
def elbow_method(X):
    wcss = []
    for i in range(1, 15):
        kmeans = KMeans(
            n_clusters=i, init="k-means++", max_iter=300, n_init=10, random_state=42
        )
        kmeans.fit(X)
        wcss.append(kmeans.inertia_)
    plt.plot(range(1, 15), wcss)
    plt.title("Elbow Method")
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


# Topic Modeling using LDA
def suggest_topics(X, feature_names, num_topics=5):
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(X)
    for index, topic in enumerate(lda.components_):
        print(f"Topic {index}:")
        print([feature_names[i] for i in topic.argsort()[-10:]])
        print("\n")


# 3D Scatter plot of the clusters using PCA
def plot_clusters_pca_3d(X, labels, num_clusters):
    pca = PCA(n_components=3)
    reduced_data = pca.fit_transform(X.toarray())

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")

    for i in range(num_clusters):
        points = reduced_data[labels == i]
        ax.scatter(points[:, 0], points[:, 1], points[:, 2], label=f"Cluster {i}")

    ax.set_title("K-Means Clustering of Emails (PCA-reduced, 3D)")
    ax.set_xlabel("PCA Component 1")
    ax.set_ylabel("PCA Component 2")
    ax.set_zlabel("PCA Component 3")
    # ax.set_zlabel("PCA Component 3")
    ax.legend()
    plt.show()


# Main processing
directory = "data"  # Replace with your directory
filter_words = [
    "enron",
    "subject",
    "http",
    "www",
    "net",
    "com",
]

emails = load_emails(directory)
preprocessed_emails = [preprocess_email(email, filter_words) for email in emails]

# Vectorize the text data
vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
X = vectorizer.fit_transform(preprocessed_emails)

# Determine the optimal number of clusters
elbow_method(X)
silhouette_analysis(X)

# Suggest possible topics
suggest_topics(X, vectorizer.get_feature_names_out(), num_topics=5)

# Apply K-Means clustering
num_clusters = 9
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
kmeans.fit(X)

# Assign emails to clusters
labels = kmeans.labels_
df = pd.DataFrame({"Email": preprocessed_emails, "Cluster": labels})


# Generate word clouds and top words for each cluster
for i in range(num_clusters):
    cluster_text = " ".join(df[df["Cluster"] == i]["Email"])

    # Generate word cloud
    generate_wordcloud(cluster_text, i)

    # Display top words
    top_words = get_top_words(cluster_text, 10)
    print(f"Top words in Cluster {i}:")
    for word, freq in top_words:
        print(f"{word}: {freq}")
    print("\n")

# Plot clusters on a scatterplot using PCA
plot_clusters_pca_3d(X, labels, num_clusters)
