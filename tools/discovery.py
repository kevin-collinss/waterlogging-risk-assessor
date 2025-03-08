#!/usr/bin/env python3
"""
explore_data.py

This script loads the training data, performs exploratory data analysis (EDA),
and outputs insights to help identify potential data issues. It includes analysis 
of both numeric features and categorical variables (Hydrology_Category and Texture) by converting
them to numeric values for plotting.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    # ------------------------------
    # 1. Load the dataset
    # ------------------------------
    data_path = "../data/training_data.csv"  # Update if needed
    df = pd.read_csv(data_path)
    
    print(f"Data loaded from {data_path}. Shape: {df.shape}")
    print("\n--- First 5 rows ---")
    print(df.head())

    # ------------------------------
    # 2. Basic Data Info
    # ------------------------------
    print("\n--- Data Info ---")
    df.info()

    print("\n--- Statistical Summary (numeric columns) ---")
    print(df.describe())

    # ------------------------------
    # 3. Check for Missing Values
    # ------------------------------
    print("\n--- Missing Values per Column ---")
    print(df.isna().sum())

    # ------------------------------
    # 4. Check for Duplicates
    # ------------------------------
    duplicates = df.duplicated()
    num_duplicates = duplicates.sum()
    print(f"\n--- Number of Duplicate Rows: {num_duplicates} ---")
    if num_duplicates > 0:
        print("Showing first few duplicate rows:")
        print(df[duplicates].head())

    # ------------------------------
    # 5. Convert Categorical Variables to Numeric
    # ------------------------------
    # For Hydrology_Category, assume you already have an encoding (e.g., Hydrology_scaled)
    # For Texture, perform label encoding if it exists
    if 'Texture' in df.columns:
        df['Texture_encoded'] = df['Texture'].astype('category').cat.codes
        print("\nTexture encoding mapping:")
        print(dict(enumerate(df['Texture'].astype('category').cat.categories)))
    else:
        print("\nNo Texture column found.")

    # ------------------------------
    # 6. Prepare a List of Numeric Columns for Plotting
    # ------------------------------
    # We'll include a selection of numeric features: Elevation, Annual_Rainfall,
    # Hydrology_scaled, Runoff_Index, and Texture_encoded (if available)
    numeric_cols = []
    for col in ['Elevation', 'Annual_Rainfall', 'Hydrology_scaled', 'Runoff_Index']:
        if col in df.columns:
            numeric_cols.append(col)
    if 'Texture_encoded' in df.columns:
        numeric_cols.append('Texture_encoded')
    
    print("\nNumeric columns selected for plotting:", numeric_cols)

    # ------------------------------
    # 7. Distribution Plots for Numeric Features
    # ------------------------------
    print("\n--- Plotting Histograms for Numeric Features ---")
    df[numeric_cols].hist(figsize=(12, 8), bins=20)
    plt.suptitle("Histogram of Numeric Features")
    plt.tight_layout()
    plt.show()

    # ------------------------------
    # 8. Correlation Heatmap for Numeric Features
    # ------------------------------
    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr()
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap='viridis', fmt=".2f")
        plt.title("Correlation Heatmap of Selected Numeric Features")
        plt.show()

    # ------------------------------
    # 9. Boxplots for Outlier Detection (Numeric Columns)
    # ------------------------------
    plt.figure(figsize=(12, 6))
    for i, col in enumerate(numeric_cols, 1):
        plt.subplot(1, len(numeric_cols), i)
        sns.boxplot(y=df[col], color='skyblue')
        plt.title(col)
    plt.tight_layout()
    plt.show()

    # ------------------------------
    # 10. Categorical Column Summaries and Count Plots
    # ------------------------------
    # Also show count plots for Hydrology_Category and Texture (original values)
    categorical_cols = []
    for col in ['Hydrology_Category', 'Texture']:
        if col in df.columns:
            categorical_cols.append(col)
    
    print("\n--- Categorical Columns Summary ---")
    for cat_col in categorical_cols:
        print(f"\nValue counts for {cat_col}:")
        print(df[cat_col].value_counts(dropna=False))
        plt.figure(figsize=(8, 4))
        sns.countplot(data=df, x=cat_col, order=df[cat_col].value_counts().index, palette='viridis')
        plt.title(f"Count Plot for {cat_col}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    print("\nExploratory data analysis complete.")

if __name__ == "__main__":
    main()
