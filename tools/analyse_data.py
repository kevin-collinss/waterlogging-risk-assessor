import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import silhouette_score, silhouette_samples, davies_bouldin_score, calinski_harabasz_score, pairwise_distances
import warnings
warnings.filterwarnings("ignore")

# ------------------------------
# Custom Dunn Index Function
# ------------------------------
def dunn_index(X, labels):
    unique_labels = np.unique(labels)
    intra_dists = []
    for label in unique_labels:
        cluster_points = X[labels == label]
        if len(cluster_points) > 1:
            dists = pairwise_distances(cluster_points)
            intra_dists.append(np.max(dists))
    if len(intra_dists) == 0:
        return np.nan
    max_intra = np.max(intra_dists)
    
    inter_dists = []
    for i in range(len(unique_labels)):
        for j in range(i+1, len(unique_labels)):
            points_i = X[labels == unique_labels[i]]
            points_j = X[labels == unique_labels[j]]
            dists = pairwise_distances(points_i, points_j)
            inter_dists.append(np.min(dists))
    if len(inter_dists) == 0:
        return np.nan
    min_inter = np.min(inter_dists)
    
    return min_inter / max_intra

# ------------------------------
# Custom Gap Statistic Function (Simplified)
# ------------------------------
def gap_statistic(X, labels, nrefs=10):
    from sklearn.cluster import KMeans
    def compute_wk(X, labels):
        unique_labels = np.unique(labels)
        Wk = 0
        for label in unique_labels:
            cluster_points = X[labels == label]
            if len(cluster_points) > 1:
                dists = pairwise_distances(cluster_points)
                Wk += np.sum(dists) / (2 * len(cluster_points))
        return Wk

    shape = X.shape
    mins = np.min(X, axis=0)
    maxs = np.max(X, axis=0)
    Wks = compute_wk(X, labels)
    Wkrefs = np.zeros(nrefs)
    
    for i in range(nrefs):
        X_ref = np.random.uniform(mins, maxs, shape)
        k = len(np.unique(labels))
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        ref_labels = km.fit_predict(X_ref)
        Wkrefs[i] = compute_wk(X_ref, ref_labels)
    
    gap = np.mean(np.log(Wkrefs)) - np.log(Wks)
    return gap

# ------------------------------
# Load Clustered Data
# ------------------------------
df = pd.read_csv("../data/training_data_with_clusters.csv")
print("Columns in the dataset:")
print(df.columns.tolist())

# ------------------------------
# Ensure Numeric Conversion for Evaluation Features
# ------------------------------
eval_features = ["Flood_Risk_Index", "Runoff_Index", "Raw_Hydrology"]
for col in eval_features:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ------------------------------
# Use features as stored in the CSV (already scaled)
# ------------------------------
X = df[eval_features].values

# ------------------------------
# Descriptive Statistics for Clustering
# ------------------------------
cluster_method = "Cluster"  # using clustering results stored in the "Cluster" column
if cluster_method in df.columns:
    print(f"\n=== Descriptive Statistics for {cluster_method} ===")
    cluster_summary = df.groupby(cluster_method)[eval_features].mean()
    print("Mean values per cluster:")
    print(cluster_summary)
    
    cluster_median = df.groupby(cluster_method)[eval_features].median()
    print("\nMedian values per cluster:")
    print(cluster_median)
    
    for cluster, group in df.groupby(cluster_method):
        print(f"\n{cluster_method} - Cluster {cluster} Raw_Hydrology distribution:")
        print(group["Raw_Hydrology"].value_counts())
else:
    print(f"Column '{cluster_method}' not found in the data.")

# ------------------------------
# Evaluation Metrics for Clustering
# ------------------------------
if cluster_method in df.columns:
    labels = df[cluster_method].values
    try:
        sil_score = silhouette_score(X, labels)
        db_index = davies_bouldin_score(X, labels)
        ch_index = calinski_harabasz_score(X, labels)
        dunn = dunn_index(X, labels)
        gap = gap_statistic(X, labels, nrefs=10)
        print(f"\nEvaluation for {cluster_method}:")
        print("Overall Silhouette Score:", sil_score)
        print("Davies–Bouldin Index:", db_index)
        print("Calinski–Harabasz Index:", ch_index)
        print("Dunn Index:", dunn)
        print("Gap Statistic:", gap)
    except Exception as e:
        print(f"Error computing metrics for {cluster_method}: {e}")
    
    sample_silhouette_values = silhouette_samples(X, labels)
    df[f"Silhouette_{cluster_method}"] = sample_silhouette_values
    
    plt.figure(figsize=(8, 6))
    sns.boxplot(x=cluster_method, y=f"Silhouette_{cluster_method}", data=df, palette="viridis")
    plt.title(f"Silhouette Score Distribution per Cluster for {cluster_method}")
    plt.xlabel("Cluster")
    plt.ylabel("Silhouette Score")
    plt.show()
else:
    print(f"Skipping evaluation for '{cluster_method}' as it is not in the data.")

# ------------------------------
# Pairplot for Visual Analysis of Composite Features
# ------------------------------
if cluster_method in df.columns:
    sns.pairplot(df, vars=eval_features, hue=cluster_method, palette="viridis", diag_kind="kde")
    plt.suptitle(f"Pairplot of Composite Features Colored by {cluster_method}", y=1.02)
    plt.show()
