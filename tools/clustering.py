import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.metrics import pairwise_distances
import warnings
warnings.filterwarnings("ignore")

# ------------------------------
# Data Loading and Preprocessing
# ------------------------------
df = pd.read_csv("../data/training_data.csv")
df = df[~df["Hydrology_Category"].isin(["Water", "Made"])]

# Save original hydrology strings before mapping
df["Hydrology_Category_Original"] = df["Hydrology_Category"]

# Select relevant columns for clustering (Texture is kept for reference; clustering uses Elevation, Annual_Rainfall, Hydrology_Category)
columns_to_use = ["Elevation", "Annual_Rainfall", "Hydrology_Category"]

# Ordinal mapping for Hydrology_Category (explicit mapping)
mapping = {"Well Drained": 0, "AlluvMIN": 1, "Peat": 2, "Poorly Drained": 3}
df["Hydrology_Category"] = df["Hydrology_Category"].map(mapping)

# Standardise numerical data (Elevation, Annual_Rainfall)
scaler = StandardScaler()
df_scaled = df.copy()
df_scaled[["Elevation", "Annual_Rainfall"]] = scaler.fit_transform(df_scaled[["Elevation", "Annual_Rainfall"]])

# ------------------------------
# Create Raw Hydrology and Apply Weighting
# ------------------------------
# Compute Raw_Hydrology by multiplying the mapped hydrology by 2
df_scaled["Raw_Hydrology"] = df["Hydrology_Category"] * 2
# Elevation remains as scaled (you may adjust weighting if desired)
df_scaled["Elevation"] = df_scaled["Elevation"]

# ------------------------------
# Compute Composite Indices
# ------------------------------
df_scaled["Flood_Risk_Index"] = df_scaled["Annual_Rainfall"] - df_scaled["Elevation"]
df_scaled["Runoff_Index"] = (3 - df_scaled["Raw_Hydrology"]) - df_scaled["Elevation"]

# ------------------------------
# Build Final Feature Matrix for Clustering
# ------------------------------
final_features = ["Flood_Risk_Index", "Runoff_Index", "Raw_Hydrology"]
X = df_scaled[final_features]

# ------------------------------
# Determine Optimal Number of Clusters via Silhouette Score (using Agglomerative Clustering)
# ------------------------------
silhouette_scores = []
k_values = range(3, 10)  # try k from 3 to 9
for k in k_values:
    agg_temp = AgglomerativeClustering(n_clusters=k)
    labels_temp = agg_temp.fit_predict(X)
    score = silhouette_score(X, labels_temp)
    silhouette_scores.append(score)
optimal_k = k_values[silhouette_scores.index(max(silhouette_scores))]
print(f"Agglo: Optimal number of clusters (k) based on silhouette score: {optimal_k}")

# ------------------------------
# Agglomerative Clustering
# ------------------------------
agglo = AgglomerativeClustering(n_clusters=optimal_k)
df_scaled["Cluster"] = agglo.fit_predict(X)

# ------------------------------
# Dimensionality Reduction for Visualization (PCA and t-SNE)
# ------------------------------
# PCA Visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)
df_scaled["PC1_PCA"] = X_pca[:, 0]
df_scaled["PC2_PCA"] = X_pca[:, 1]

plt.figure(figsize=(8, 6))
sns.scatterplot(data=df_scaled, x="PC1_PCA", y="PC2_PCA", hue="Cluster", palette="viridis", s=100)
plt.title(f"PCA Visualization (Agglomerative, k={optimal_k})")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.legend(title="Cluster")
plt.show()

# t-SNE Visualization
tsne = TSNE(n_components=2, perplexity=30, random_state=42)
X_tsne = tsne.fit_transform(X)
df_scaled["TSNE1"] = X_tsne[:, 0]
df_scaled["TSNE2"] = X_tsne[:, 1]

plt.figure(figsize=(8, 6))
sns.scatterplot(data=df_scaled, x="TSNE1", y="TSNE2", hue="Cluster", palette="viridis", s=100)
plt.title(f"t-SNE Visualization (Agglomerative, k={optimal_k})")
plt.xlabel("t-SNE Dimension 1")
plt.ylabel("t-SNE Dimension 2")
plt.legend(title="Cluster")
plt.show()

# ------------------------------
# Silhouette Analysis and Plotting Function
# ------------------------------
def plot_silhouette(X, labels, method_name):
    sil_avg = silhouette_score(X, labels)
    sil_vals = silhouette_samples(X, labels)
    print(f"\n{method_name} - Average Silhouette Score: {sil_avg:.4f}")
    
    plt.figure(figsize=(8, 6))
    y_lower = 10
    n_clusters = len(np.unique(labels))
    for i in np.unique(labels):
        ith_vals = sil_vals[labels == i]
        ith_vals.sort()
        size_i = ith_vals.shape[0]
        y_upper = y_lower + size_i
        plt.fill_betweenx(np.arange(y_lower, y_upper), 0, ith_vals, alpha=0.7)
        plt.text(-0.05, y_lower + 0.5 * size_i, str(i))
        y_lower = y_upper + 10
    plt.axvline(x=sil_avg, color="red", linestyle="--")
    plt.xlabel("Silhouette Score")
    plt.ylabel("Cluster Label")
    plt.title(f"Silhouette Plot for {method_name} (n_clusters = {n_clusters})")
    plt.show()

plot_silhouette(X, df_scaled["Cluster"].values, "Agglomerative Clustering")

# ------------------------------
# Revert Hydrology_Category back to original string values before saving
# ------------------------------
df_scaled["Hydrology_Category"] = df["Hydrology_Category_Original"]

# ------------------------------
# Save the Labelled Data to CSV
# ------------------------------
output_path = "../data/training_data_with_clusters.csv"
df_scaled.to_csv(output_path, index=False)
print(f"\nClustered data saved to {output_path}")
