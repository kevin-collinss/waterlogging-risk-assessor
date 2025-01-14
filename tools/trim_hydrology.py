import pandas as pd

# Input and output file paths
input_csv = "data/hydrology_data_full.csv"  # Replace with the path to your original CSV
output_csv = "data/hydrology_data_trimmed.csv"  # Path to save the trimmed CSV

# Columns to retain
columns_to_keep = ["CATEGORY", "ParMat_Des", "SoilDraina", "geometry"]

try:
    # Load the CSV file into a DataFrame
    df = pd.read_csv(input_csv)

    # Check if all required columns exist in the input CSV
    missing_columns = [col for col in columns_to_keep if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in input CSV: {', '.join(missing_columns)}")

    # Select only the required columns
    trimmed_df = df[columns_to_keep]

    # Save the trimmed DataFrame to a new CSV
    trimmed_df.to_csv(output_csv, index=False)

    print(f"Trimmed CSV saved to {output_csv}")

except FileNotFoundError:
    print(f"Error: File not found at {input_csv}")
except Exception as e:
    print(f"An error occurred: {e}")
