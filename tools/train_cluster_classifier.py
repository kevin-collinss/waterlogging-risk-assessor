import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

file_path = "../data/training_data_with_clusters.csv"
df = pd.read_csv(file_path)

# Drop redundant columns: Description, visualization columns, and any extra computed features
columns_to_drop = ["Description", "PC1_PCA", "PC2_PCA", "TSNE1", "TSNE2", 
                   "Raw_Hydrology", "Flood_Risk_Index", "Runoff_Index", "Elev_Hydro_PCA"]
for col in columns_to_drop:
    if col in df.columns:
        df = df.drop(columns=[col])

texture_encoder = LabelEncoder()
hydrology_encoder = LabelEncoder()

df["Texture"] = texture_encoder.fit_transform(df["Texture"])
df["Hydrology_Category"] = hydrology_encoder.fit_transform(df["Hydrology_Category"])

# Save encoders for future use
joblib.dump(texture_encoder, "../models/texture_encoder.pkl")
joblib.dump(hydrology_encoder, "../models/hydrology_encoder.pkl")

X = df[["Texture", "Elevation", "Annual_Rainfall", "Hydrology_Category"]]
y = df["Cluster"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, "../models/scaler.pkl")

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

models = {
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "SVM": SVC(kernel="linear", probability=True, random_state=42),
    "k-NN": KNeighborsClassifier(n_neighbors=5),
    "Logistic Regression": LogisticRegression(max_iter=500, random_state=42)
}

best_model = None
best_accuracy = 0
results = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    results[name] = acc

    print(f"\n{name} Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred))
    
    if acc > best_accuracy:
        best_accuracy = acc
        best_model = model
        best_model_name = name

model_path = "../models/best_cluster_classifier.pkl"
joblib.dump(best_model, model_path)
print(f"\nBest model: {best_model_name} (Accuracy: {best_accuracy:.4f}) saved to {model_path}")
