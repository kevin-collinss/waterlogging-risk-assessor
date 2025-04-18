# Waterlogging Risk Assessor

# Tech Breakdown: Waterlogging Risk Classifier

This document provides a detailed explanation of the technical design, algorithms, and tools used to create the Waterlogging Risk Classifier. The goal of this tool is to help farmers, researchers, and planners better understand waterlogging and flood risk on agricultural land in Ireland using real-world environmental data and machine learning.

---

## 1. Data Collection and Preprocessing

The dataset used for training the model is generated using a custom script (`training_dataset.py`) that:

- Randomly samples geographic coordinates (Easting, Northing) across Ireland using Irish Grid bounds.
- Queries a backend Flask API (`/get_data`) for each sampled point, returning:
  - **Soil texture and description**
  - **Elevation**
  - **Annual rainfall**
  - **Hydrology category**
- Filters out incomplete or invalid points.
- Writes structured, valid entries to `training_data.csv`.

### Example structure of collected fields:
- `Easting`, `Northing`
- `Texture`, `Description`
- `Elevation`, `Annual_Rainfall`
- `Hydrology_Category`

---

## 2. Feature Engineering & Clustering (Unsupervised Learning)

The script `clustering.py` processes the raw dataset and performs unsupervised learning to group fields into meaningful waterlogging risk clusters.

### Preprocessing Steps
- Removes unwanted categories (`Water`, `Made`).
- Applies ordinal encoding to categorical values (e.g., `Hydrology_Category`).
- Standardises features like `Elevation` and `Annual_Rainfall`.
- Introduces two domain-specific indices:
  - **Flood Risk Index**: `Annual_Rainfall - Elevation`
  - **Runoff Index**: A custom formula incorporating soil drainage potential.


### Elbow Method for Optimal Clusters
The elbow method is a commonly used technique to determine the optimal number of clusters. It plots the inertia (or within-cluster sum of squares) against the number of clusters. The optimal point corresponds to the "elbow" of the curve, where the inertia starts to decrease more slowly.

![Elbow Method](../images/markdown/elbow_method.png)

### Clustering
We use **Agglomerative Clustering**, a hierarchical algorithm, to group data points based on similarity in environmental attributes.

- Silhouette scores are computed to determine the optimal number of clusters (typically 4).
- Each point is assigned a cluster label (0–3), corresponding to flood risk levels.

### Silhouette Score for Clustering
The silhouette score provides a single score to evaluate the clustering quality, considering both the cohesion (how close points are within their cluster) and separation (how well-separated the clusters are).

![Silhouette Score](../images/markdown/silhouette_score.png)

### Silhouette Plot for Clustering Evaluation
The silhouette score measures how similar each point is to its own cluster compared to other clusters. A higher score indicates better-defined clusters. The silhouette plot below shows the scores for each data point in the clusters.

![Silhouette Plot](../images/markdown/silhouette_plot.png)

This Silhouette Plot for Agglomerative Clustering shows how well-separated and well-formed each cluster is. The silhouette score ranges from -1 to +1, where a higher score indicates better-defined clusters. The red dashed line represents the average silhouette score (0.6), which suggests good clustering overall.

Cluster 3 (yellow) and Cluster 2 (green) show strong separation, while Cluster 1 (blue) is slightly less distinct.

Cluster 0 (purple) has the lowest silhouette score, suggesting it is less cohesive or potentially misclassified.

### Dendrogram: Visualising Hierarchical Clustering

To better understand how the clustering algorithm grouped different environmental points, we generated a dendrogram. This visual shows the hierarchical structure of how similar data points are merged during the agglomerative clustering process.

![Dendrogram of Clustering Process](/images/markdown/dendrogram_plot.png)

This Dendrogram for Agglomerative Clustering provides insight into the hierarchical relationships between the data points. The blue line represents the final split between the first two major clusters.

The orange cluster is more fragmented, indicating the presence of several sub-clusters within it.

The green cluster is more compact, suggesting a tighter grouping of data points.

The analysis reveals that four distinct clusters are formed after considering the dendrogram's structure, as indicated by the splitting of the clusters at the appropriate Euclidean distance. 

### Pairplot for Clustering Visualization
A pairplot provides a matrix of scatter plots that show relationships between each pair of features. It can reveal if the clusters are separable and if the features are correlated.

![Pairplot](../images/markdown/pairplot.png)

## Visualisation
For interpretability, clustering results are projected into 2D using:

### PCA Visualization
Principal Component Analysis (PCA) reduces the dimensionality of the dataset while preserving as much variance as possible. This plot shows the clustering results in the reduced 2D space defined by the first two principal components.

![PCA Plot](../images/markdown/pca_plot.png)

### t-SNE Visualization
t-SNE is another dimensionality reduction technique that helps visualize high-dimensional data in two dimensions. This plot shows how well the clusters are separated after applying t-SNE.

![t-SNE Plot](../images/markdown/tsne_plot.png)

These plots allow us to visually verify the separation and density of each cluster.

---

## 3. Classifier Training (Supervised Learning)

The script `train_cluster_classifier.py` trains a **supervised machine learning model** that learns to predict the cluster label from raw features — enabling predictions on new unseen locations.

### Features used:
- Soil Texture (encoded)
- Elevation (scaled)
- Annual Rainfall (scaled)
- Hydrology Category (encoded)

### Model Training Workflow:
1. Split data into train and test sets (80/20).
2. Train 4 classifiers:  
   - **Random Forest**  
   - **Support Vector Machine (SVM)**  
   - **K-Nearest Neighbours (kNN)**  
   - **Logistic Regression**
3. Evaluate each using accuracy and classification report.
4. Save the best-performing model using `joblib`.

The winning model is saved as:  

/models/best_cluster_classifier.pkl

---
## 4. Backend API Server

The backend server is implemented using **Node.js** with the **Express.js** framework. Its core responsibility is to act as a bridge between the frontend map interface and the Python-based data and machine learning logic.

### Responsibilities:
- Accepts incoming requests from the frontend containing location coordinates.
- Executes a Python script (`get_data.py`) to retrieve environmental and predictive information.
- Sends back a structured JSON response with all relevant data.

### How it Works:
When a user clicks a location on the map:
1. The Mapbox frontend extracts the longitude and latitude of the clicked point.
2. These coordinates are converted to Irish Grid (EPSG:29903).
3. A POST request is made to the Express endpoint `/get_data` with the easting and northing values.
4. `server.js` runs `get_data.py` using `child_process.exec`, passing the coordinates as arguments.
5. The Python script:
   - Loads environmental data from preprocessed sources or live queries.
   - Uses the trained classifier model to predict the waterlogging cluster.
   - Returns all relevant attributes (e.g. soil, rainfall, hydrology, elevation).
6. The JSON response is returned to the frontend to populate the right-hand sidebar.

### Example Response:
```json
{
  "soil_data": {
    "Texture_Su": "Peat",
    "DEPTH": "50-100cm",
    "PlainEngli": "Dark, organic-rich soil"
  },
  "hydrology_data": {
    "CATEGORY": "Poorly Drained",
    "ParMat_Des": "Peat/Clay",
    "SoilDraina": "Low"
  },
  "elevation_data": {
    "Elevation": 122.5
  },
  "rainfall_data": {
    "ANN": 1300,
    "DJF": 420,
    "MAM": 290,
    "JJA": 280,
    "SON": 310
  },
  "cluster_prediction": 2
}
```
---

## 5. Interactive Frontend (Mapbox)

The interactive frontend interface is built using **React** and **Mapbox GL JS** and serves as the primary point of interaction for users exploring flood risk. It allows users to click on any location in Ireland and retrieve predictions and environmental context for that area.

### Key Features

- **Satellite-Street Map Layer:** The interface uses Mapbox's `satellite-streets-v11` basemap for a rich, real-world view.
- **Click Interaction:** When a user clicks on the map, their coordinates are captured and converted to Irish Grid format (EPSG:29903) using the `proj4` library.
- **Live Data Fetching:** A POST request is sent to the backend with easting and northing values. The server responds with environmental data and a predicted cluster.
- **Sidebar Display:** A responsive sidebar presents the prediction results, including:
  - Predicted cluster and associated waterlogging risk label.
  - Soil characteristics.
  - Hydrology classification.
  - Elevation in metres.
  - Seasonal and annual rainfall data.
- **Map Stamp Visualisation:** A circular "stamp" image is overlaid on the map to indicate the area the user clicked on for analysis.

### Cluster Risk Mapping

Each predicted cluster maps to a predefined waterlogging risk category:

| Cluster | Risk Level         | Colour     |   
|---------|--------------------|------------|   
| 0       | Low                | Purple     |   
| 1       | Moderate to High   | Blue       |   
| 2       | Moderate           | Green      |   
| 3       | Low to Moderate    | Yellow     |   


---

## 6. Cluster Visualisation (Leaflet)

The `LeafletPointMap.js` component is an alternative interface for viewing all training data points and their cluster classifications. It is built with **React-Leaflet**, a wrapper around the Leaflet.js library, known for its light-weight mapping performance.

### Key Features

- **Dataset Integration:** Points are sourced from the `training_data_with_clusters.csv` file, which contains pre-labelled training data.
- **Coordinate Transformation:** Points stored in Irish Grid format (EPSG:29903) are transformed into WGS84 (EPSG:4326) using the `proj4` library before rendering.
- **Point Rendering:** All points are rendered as `CircleMarker` elements with fixed radii and colour-coded styling based on their cluster label.
- **Performance Optimisation:** Leaflet’s lightweight rendering makes it suitable for displaying thousands of small markers simultaneously.

This map allows users to visually understand how the unsupervised learning algorithm has segmented the Irish landscape by flood risk, and compare spatial patterns across the country.

