import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import warnings
warnings.filterwarnings("ignore")

# ------------------------------
# Data Loading and Preprocessing
# ------------------------------
df = pd.read_csv("../data/training_data.csv")
df = df[~df["Hydrology_Category"].isin(["Water", "Made"])]
df["Hydrology_Category_Original"] = df["Hydrology_Category"]

mapping = {"Well Drained": 0, "AlluvMIN": 1, "Peat": 2, "Poorly Drained": 3}
df["Hydrology_Category"] = df["Hydrology_Category"].map(mapping)

scaler = StandardScaler()
df_scaled = df.copy()
df_scaled[["Elevation", "Annual_Rainfall"]] = scaler.fit_transform(df_scaled[["Elevation", "Annual_Rainfall"]])

df_scaled["Raw_Hydrology"] = df["Hydrology_Category"] * 2
df_scaled["Flood_Risk_Index"] = df_scaled["Annual_Rainfall"] - df_scaled["Elevation"]
df_scaled["Runoff_Index"] = (3 - df_scaled["Raw_Hydrology"]) - df_scaled["Elevation"]

X = df_scaled[["Flood_Risk_Index", "Runoff_Index", "Raw_Hydrology"]]

silhouette_scores = []
k_values = range(3, 10)
for k in k_values:
    agg_temp = AgglomerativeClustering(n_clusters=k)
    labels_temp = agg_temp.fit_predict(X)
    score = silhouette_score(X, labels_temp)
    silhouette_scores.append(score)

optimal_k = k_values[silhouette_scores.index(max(silhouette_scores))]
agglo = AgglomerativeClustering(n_clusters=optimal_k)
labels = agglo.fit_predict(X)
df_scaled["Cluster"] = labels

pca = PCA(n_components=2)
pca_result = pca.fit_transform(X)
df_scaled["PCA1"] = pca_result[:, 0]
df_scaled["PCA2"] = pca_result[:, 1]

# t-SNE
tsne = TSNE(n_components=2, perplexity=30, random_state=42)
tsne_result = tsne.fit_transform(X)
df_scaled["TSNE1"] = tsne_result[:, 0]
df_scaled["TSNE2"] = tsne_result[:, 1]

# Plot
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

sns.scatterplot(data=df_scaled, x="PCA1", y="PCA2", hue="Cluster", palette="viridis", s=60, ax=axes[0])
axes[0].set_title("PCA Projection")
axes[0].set_xlabel("PC1")
axes[0].set_ylabel("PC2")
axes[0].legend(title="Cluster", loc='best')

sns.scatterplot(data=df_scaled, x="TSNE1", y="TSNE2", hue="Cluster", palette="viridis", s=60, ax=axes[1])
axes[1].set_title("t-SNE Projection")
axes[1].set_xlabel("t-SNE 1")
axes[1].set_ylabel("t-SNE 2")
axes[1].legend(title="Cluster", loc='best')

plt.tight_layout()
plt.savefig("../frontend/frontend/public/images/markdown/pca_tsne_clusters.png")
plt.close()
