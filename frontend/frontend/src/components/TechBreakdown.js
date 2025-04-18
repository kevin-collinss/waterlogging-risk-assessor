import React from 'react';
import { Link } from 'react-router-dom';
import 'github-markdown-css';

const TechBreakdown = () => {
  return (
    <div style={{ padding: '40px' }}>
      <Link to="/map" className="fixed-back-button">
        ← Back to Map
      </Link>

      <div className="markdown-body" style={{ marginTop: '20px' }}>
        <h1>Field Flood and Waterlogging Risk Analysis System</h1>
        <p>The Field Flood and Waterlogging Risk Analysis System is a technical solution developed to address the increasing risk of waterlogging across Irish agricultural land. The motivation behind the system stems from observable environmental changes — in particular, heavier and more persistent rainfall patterns, and increasing soil saturation. Current government flood risk tools offer regional-scale insights and are unsuitable for decision-making at the individual field level. This system bridges that gap through a combination of geospatial data, clustering algorithms, and a machine learning-based classification framework, ultimately serving farmers and planners with detailed, interpretable insights.</p>

        <h2>The Data</h2>
        <ul>
          <li>Each data point represents a unique field-scale sample from across the Republic of Ireland, supporting a highly granular modelling approach.</li>
          <li>Four primary datasets were integrated:
            <ul>
              <li>Topographic elevation data from NASA</li>
              <li>Annual rainfall figures from Met Éireann</li>
              <li>Soil texture and hydrology from the Teagasc Irish Soil Information System (ISIS)</li>
            </ul>
          </li>
          <li>All datasets were originally provided in different spatial reference systems (e.g., WGS84, UTM, Irish Grid), which required harmonisation.</li>
          <li>To ensure alignment and spatial consistency, all features were transformed into the EPSG:29903 Irish Grid projection before processing.</li>
          <li>Invalid or incomplete records were removed to produce a final cleaned dataset suitable for both clustering and real-time inference.</li>
        </ul>

        <p>To gather data for clustering I created a script to get 10,000 points across Ireland.</p>
        <div>
          <img src="/images/markdown/default_map.png" alt="Default Map" width="700" />
        </div>

        <hr />
        <h2>Feature Engineering</h2>
        <ul>
          <li>The dataset excluded entries with hydrology categories labelled "Water" or "Made" to remove artificial or unreliable entries.</li>
          <li>Hydrology categories were ordinally encoded using expert-informed mappings to better reflect their physical properties.</li>
          <li>Elevation and annual rainfall values were standardised to ensure equal weighting during clustering.</li>
          <li>A new field called <strong>Raw Hydrology</strong> was computed by multiplying the encoded hydrology value by 2 — this increased its influence in further calculations.</li>
          <li><strong>Flood Risk Index</strong> was calculated as <code>Annual Rainfall - Elevation</code>, representing a proxy for water accumulation potential.</li>
          <li><strong>Runoff Index</strong> was defined as <code>(3 - Raw Hydrology) - Elevation</code>, integrating drainage potential with elevation drop to estimate runoff sensitivity.</li>
          <li>The feature matrix <code>X</code> used for clustering included Flood Risk Index, Runoff Index, and Raw Hydrology — all engineered variables with practical environmental interpretations.</li>
        </ul>

        <h2>Clustering Process and Analysis</h2>
        <p>Unsupervised learning was used to identify natural risk zones in the Irish agricultural landscape. Initial tests were run with K-Means and DBSCAN, but they showed weaknesses in identifying uneven and irregular environmental patterns. K-Means struggled with the spherical cluster assumption, while DBSCAN's density-based approach was too sensitive to parameter tuning and underperformed on sparse areas. Ultimately, Agglomerative Clustering was selected for its ability to construct a hierarchical tree of fields based on feature similarity.</p>

        <div>
        <img src="/images/markdown/sil_comparison.png" alt="Sil Comparison" width="700" />
        </div>


        <img src="/images/markdown/elbow_method.png" alt="Elbow Method" width="700" />
        <p>The Elbow Method showed that 4 clusters represented the optimal trade-off between model complexity and inertia reduction.</p>

        <img src="/images/markdown/silhouette_score.png" alt="Silhouette Score" width="700" />
        <p>The silhouette score peaked at 4 clusters, confirming high intra-cluster similarity and inter-cluster separation.</p>

        <img src="/images/markdown/silhouette_plot.png" alt="Silhouette Plot" width="700" />
        <p>Silhouette plots highlighted that Cluster 0 was slightly noisier than the others, while Cluster 2 demonstrated excellent separation and cohesion, often corresponding to well-drained soils on elevated terrain.</p>

        <img src="/images/markdown/dendrogram_plot.png" alt="Dendrogram" width="700" />
        <p>The dendrogram provides insight into the hierarchical grouping of fields, showing which clusters were merged and when during the agglomerative process. The 4 major clusters emerge at a Euclidean height that aligns with environmental intuition.</p>

        <img src="/images/markdown/pairplot.png" alt="Pairplot" width="1000" />
        <p>This pairplot offers a multidimensional snapshot of how environmental features correlate across clusters. For example, rainfall and soil texture groupings are visible in the diagonal histograms, supporting the idea that the model is capturing interpretable environmental behaviour.</p>

        <h2>Cluster Projection and Interpretation</h2>
        <img src="/images/markdown/pca_plot.png" alt="PCA Plot" width="700" />
        <p>The PCA projection shows the clustering behaviour in reduced 2D space. Clusters 1 and 2 appear as compact, tightly grouped regions, suggesting highly distinguishable environmental profiles, while Cluster 0 spans a broader region with less internal coherence.</p>

        <img src="/images/markdown/tsne_plot.png" alt="t-SNE Plot" width="700" />
        <p>The t-SNE visualisation confirms the separation seen in PCA, but better highlights local grouping within each cluster. It's particularly effective at illustrating overlapping fields that may share flood or drainage profiles.</p>

        <img src="/images/markdown/cluster_eval.png" alt="Cluster Evaluation" width="700" />
        <p>The final cluster evaluation summary provides a quantitative assessment: a silhouette score of 0.595 suggests strong cluster structure, while the Davies-Bouldin and Dunn indices show strong separation and minimal overlap. The high Calinski-Harabasz score further supports the compactness of clusters.</p>

        <img src="/images/data_origin.png" alt="Data Origin" width="700" />

        <h2>Classifier Design and Evaluation</h2>
        <p>Once clusters were assigned, the challenge was enabling real-time predictions for new unseen fields. Since clustering is unsupervised and does not generalise beyond training data, a supervised classification model was introduced post-clustering. This model learns to replicate the cluster assignments based on the environmental features. Multiple classifiers were tested, including Logistic Regression, SVM, and k-NN, but Random Forest delivered the best balance of accuracy and generalisability.</p>

        <img src="/images/markdown/confusion_matrix.png" alt="Confusion Matrix" width="700" />
        <p>The confusion matrix shows near-perfect prediction for Clusters 2 and 3. Minor confusion occurred between Clusters 0 and 1, which were both associated with moderate-risk fields. Overall, the test accuracy was 91.67% with strong precision and recall across the board.</p>

        <h2>Deployment Architecture</h2>
        <p>The model is deployed as part of a full-stack web application. The frontend is built with React and Mapbox GL JS. Users interactively click a location, triggering a request to the backend that passes the coordinate to a Python script via Node.js. The script fetches the environmental data, standardises it, and passes it to the Random Forest model to predict a flood risk cluster. The result, along with soil, elevation, and rainfall breakdowns, is returned to the frontend and displayed in a sidebar.</p>

        <h2>Expert Feedback and Future Improvements</h2>
        <p>Dr. Ken Byrne, an expert in soil science, reviewed the model outputs and confirmed that cluster definitions matched known field drainage characteristics. He recommended the addition of soil conductivity data to further improve classification reliability. Future extensions also include integrating seasonal rainfall updates and developing real-time flood forecasting capabilities.</p>
      </div>
    </div>
  );
};

export default TechBreakdown;
