import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import AgglomerativeClustering
from sklearn.manifold import TSNE
import scipy.cluster.hierarchy as sch
from sklearn.metrics import silhouette_samples, silhouette_score
import numpy as np

# Load dataset
df = pd.read_csv("../data/training_data.csv")

# Drop Easting and Northing as per request
df = df.drop(columns=["Easting", "Northing"])

# Select relevant columns for clustering
columns_to_use = ["Texture", "Elevation", "Annual_Rainfall", "Hydrology_Category"]

# Encode categorical columns (Texture, Hydrology_Category)
label_encoders = {}
for col in ["Texture", "Hydrology_Category"]:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le  # Store encoders for potential future use

# Standardise numerical data
df_scaled = df.copy()
df_scaled[["Elevation", "Annual_Rainfall"]] = StandardScaler().fit_transform(df_scaled[["Elevation", "Annual_Rainfall"]])

# Prepare features for clustering
X = df_scaled[columns_to_use]

# Plot Dendrogram to Find Optimal Clusters
plt.figure(figsize=(10, 5))
sch.dendrogram(sch.linkage(X, method="ward"))
plt.title("Dendrogram for Agglomerative Clustering")
plt.xlabel("Data Points")
plt.ylabel("Euclidean Distance")
plt.savefig("../images/dendrogram.png")
plt.show()

# Apply Agglomerative Clustering (Using Optimal Number of Clusters from Dendrogram)
n_clusters = 5  # Adjust based on dendrogram
agg_clustering = AgglomerativeClustering(n_clusters=n_clusters)
df["Cluster"] = agg_clustering.fit_predict(X)

# Apply t-SNE for visualization
tsne = TSNE(n_components=2, perplexity=30, random_state=42)
df_tsne = pd.DataFrame(tsne.fit_transform(X), columns=["tSNE1", "tSNE2"])
df_tsne["Cluster"] = df["Cluster"]

# Plot t-SNE Scatterplot of Agglomerative Clusters
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df_tsne, x="tSNE1", y="tSNE2", hue="Cluster", palette="viridis", s=100)
plt.title("Clusters Visualised with t-SNE (Agglomerative Clustering)")
plt.xlabel("t-SNE Component 1")
plt.ylabel("t-SNE Component 2")
plt.legend(title="Cluster")
plt.savefig("../images/clusters_tsne_agg.png")
plt.show()

# Compute and Plot Silhouette Scores
silhouette_avg = silhouette_score(X, df["Cluster"])
silhouette_vals = silhouette_samples(X, df["Cluster"])

plt.figure(figsize=(8, 6))
y_lower = 10
for i in range(n_clusters):
    cluster_silhouette_vals = silhouette_vals[df["Cluster"] == i]
    cluster_silhouette_vals.sort()
    size_cluster_i = cluster_silhouette_vals.shape[0]
    y_upper = y_lower + size_cluster_i
    plt.fill_betweenx(np.arange(y_lower, y_upper), 0, cluster_silhouette_vals, alpha=0.7)
    plt.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
    y_lower = y_upper + 10

plt.axvline(x=silhouette_avg, color="red", linestyle="--")
plt.xlabel("Silhouette Score")
plt.ylabel("Cluster Label")
plt.title(f"Silhouette Analysis for Agglomerative Clustering (n_clusters = {n_clusters})")
plt.savefig("../images/silhouette_plot.png")
plt.show()

print(f"Average Silhouette Score: {silhouette_avg:.4f}")

# --- Unencode categorical features before saving ---
for col in ["Texture", "Hydrology_Category"]:
    le = label_encoders[col]
    df[col] = le.inverse_transform(df[col])

# Save the Clustered Data
output_file_path = "../data/training_data_with_clusters.csv"
df.to_csv(output_file_path, index=False)
print(f"Clustered data saved to {output_file_path}")
