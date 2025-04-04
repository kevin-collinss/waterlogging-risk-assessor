import pandas as pd
import numpy as np
import time
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv("../data/training_data.csv")
df = df[~df["Hydrology_Category"].isin(["Water", "Made"])]
mapping = {"Well Drained": 0, "AlluvMIN": 1, "Peat": 2, "Poorly Drained": 3}
df["Hydrology_Category"] = df["Hydrology_Category"].map(mapping)

scaler = StandardScaler()
df_scaled = df.copy()
df_scaled[["Elevation", "Annual_Rainfall"]] = scaler.fit_transform(df[["Elevation", "Annual_Rainfall"]])
df_scaled["Raw_Hydrology"] = df["Hydrology_Category"] * 2
df_scaled["Flood_Risk_Index"] = df_scaled["Annual_Rainfall"] - df_scaled["Elevation"]
df_scaled["Runoff_Index"] = (3 - df_scaled["Raw_Hydrology"]) - df_scaled["Elevation"]

X = df_scaled[["Flood_Risk_Index", "Runoff_Index", "Raw_Hydrology"]]

results = []

# Agglomerative
start = time.time()
agg = AgglomerativeClustering(n_clusters=4)
labels_agg = agg.fit_predict(X)
score_agg = silhouette_score(X, labels_agg)
end = time.time()
results.append({
    "Method": "Agglomerative",
    "Clusters": len(np.unique(labels_agg)),
    "Noise Points": "-",
    "Silhouette Score": round(score_agg, 3),
    "Runtime (s)": round(end - start, 3)
})

# KMeans
start = time.time()
kmeans = KMeans(n_clusters=4, random_state=42)
labels_kmeans = kmeans.fit_predict(X)
score_kmeans = silhouette_score(X, labels_kmeans)
end = time.time()
results.append({
    "Method": "KMeans",
    "Clusters": len(np.unique(labels_kmeans)),
    "Noise Points": "-",
    "Silhouette Score": round(score_kmeans, 3),
    "Runtime (s)": round(end - start, 3)
})

# DBSCAN
start = time.time()
dbscan = DBSCAN(eps=0.8, min_samples=5)
labels_dbscan = dbscan.fit_predict(X)
if len(set(labels_dbscan)) > 1 and -1 in set(labels_dbscan):
    valid_idx = labels_dbscan != -1
    score_dbscan = silhouette_score(X[valid_idx], labels_dbscan[valid_idx])
else:
    score_dbscan = -1
end = time.time()
results.append({
    "Method": "DBSCAN",
    "Clusters": len(set(labels_dbscan)) - (1 if -1 in labels_dbscan else 0),
    "Noise Points": list(labels_dbscan).count(-1),
    "Silhouette Score": round(score_dbscan, 3) if score_dbscan != -1 else "N/A",
    "Runtime (s)": round(end - start, 3)
})

df_results = pd.DataFrame(results)
print("\n### Clustering Method Comparison\n")
print(df_results.to_markdown(index=False))
