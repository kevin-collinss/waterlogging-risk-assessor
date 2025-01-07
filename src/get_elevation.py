import pandas as pd
import numpy as np

# Load the Elevation Data CSV file
elevation_data_path = 'data/elevation_data.csv'  # Update the path to your file
elevation_df = pd.read_csv(elevation_data_path)


def find_closest_elevation(easting, northing):
    """
    Find the closest elevation data for a specific Easting and Northing.
    """
    if elevation_df.empty:
        raise ValueError("The elevation data file is empty or not loaded correctly.")

    # Ensure required columns exist in the DataFrame

    required_columns = {'Easting', 'Northing', 'Elevation'}

    if not required_columns.issubset(elevation_df.columns):
        raise ValueError(f"CSV is missing one or more required columns: {required_columns}")

    # Calculate the Euclidean distance to all points in the DataFrame
    elevation_df['Distance'] = np.sqrt(
        (elevation_df['Easting'] - easting) ** 2 + (elevation_df['Northing'] - northing) ** 2
    )

    # Find the row with the minimum distance
    closest_row = elevation_df.loc[elevation_df['Distance'].idxmin()]

    # Return the closest row as a dictionary
    return closest_row.to_dict()


# Example Easting and Northing to test the function
easting = 311567  # Replace with the Easting you want to search
northing = 215448  # Replace with the Northing you want to search
try:
    elevation_info = find_closest_elevation(easting, northing)
    if elevation_info:
        print("Closest Elevation Data:", elevation_info)
except ValueError as e:
    print("Error:", e)
