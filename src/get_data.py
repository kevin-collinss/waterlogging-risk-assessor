import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely import wkt

# Load the data files
soil_data = pd.read_csv("data/soil_data.csv")
hydrology_data = pd.read_csv("data/hydrology_data.csv")
elevation_data = pd.read_csv("data/elevation_data.csv")
rainfall_data = pd.read_csv("data/rainfall_data.csv")  # Ensure rainfall data CSV is available

# Parse geometry columns in soil and hydrology data
soil_data['geometry'] = soil_data['geometry'].apply(wkt.loads)
hydrology_data['geometry'] = hydrology_data['geometry'].apply(wkt.loads)

# Convert to GeoDataFrames
soil_gdf = gpd.GeoDataFrame(soil_data, geometry=soil_data['geometry'])
hydrology_gdf = gpd.GeoDataFrame(hydrology_data, geometry=hydrology_data['geometry'])

# Ensure elevation and rainfall data have no extra spaces in column names
elevation_data.rename(columns=lambda x: x.strip(), inplace=True)
rainfall_data.rename(columns=lambda x: x.strip(), inplace=True)

# Verify required columns in elevation and rainfall data
required_elevation_columns = ['Easting', 'Northing', 'Elevation']
required_rainfall_columns = ['Easting', 'Northing', 'ANN', 'DJF', 'MAM', 'JJA', 'SON']

for col in required_elevation_columns:
    if col not in elevation_data.columns:
        raise ValueError(f"Missing required column: {col} in elevation_data.csv")

for col in required_rainfall_columns:
    if col not in rainfall_data.columns:
        raise ValueError(f"Missing required column: {col} in rainfall_data.csv")

def get_combined_data(easting, northing):
    """
    Fetch combined soil, hydrology, elevation, and rainfall data for a given easting and northing.
    """
    # Create a point geometry from the provided coordinates
    point = Point(easting, northing)
    point_gdf = gpd.GeoDataFrame(index=[0], geometry=[point], crs=soil_gdf.crs)

    # Perform spatial joins for soil and hydrology data
    soil_result = gpd.sjoin(point_gdf, soil_gdf, how="inner", predicate='intersects')
    hydrology_result = gpd.sjoin(point_gdf, hydrology_gdf, how="inner", predicate='intersects')

    # Find the closest elevation point using Euclidean distance
    elevation_data['Distance'] = ((elevation_data['Easting'] - easting) ** 2 +
                                  (elevation_data['Northing'] - northing) ** 2).pow(0.5)
    closest_elevation = elevation_data.loc[elevation_data['Distance'].idxmin()]

    # Find the closest rainfall point using Euclidean distance
    rainfall_data['Distance'] = ((rainfall_data['Easting'] - easting) ** 2 +
                                 (rainfall_data['Northing'] - northing) ** 2).pow(0.5)
    closest_rainfall = rainfall_data.loc[rainfall_data['Distance'].idxmin()]

    # Extract required fields
    soil_data_result = None
    if not soil_result.empty:
        soil_record = soil_result.iloc[0]  # Get the first record
        soil_data_result = {
            "POINT": soil_record.geometry,
            "Texture_Su": soil_record.get("Texture_Su"),
            "TEXTURE": soil_record.get("TEXTURE"),
            "DEPTH": soil_record.get("DEPTH"),
            "PlainEngli": soil_record.get("PlainEngli")
        }

    hydrology_data_result = None
    if not hydrology_result.empty:
        hydrology_record = hydrology_result.iloc[0]  # Get the first record
        hydrology_data_result = {
            "CATEGORY": hydrology_record.get("CATEGORY"),
            "ParMat_Des": hydrology_record.get("ParMat_Des"),
            "SoilDraina": hydrology_record.get("SoilDraina")
        }

    elevation_data_result = {
        "Elevation": closest_elevation["Elevation"]
    }

    rainfall_data_result = {
        "ANN": closest_rainfall["ANN"],
        "DJF": closest_rainfall["DJF"],
        "MAM": closest_rainfall["MAM"],
        "JJA": closest_rainfall["JJA"],
        "SON": closest_rainfall["SON"]
    }

    # Combine results
    result = {
        "soil_data": soil_data_result,
        "hydrology_data": hydrology_data_result,
        "elevation_data": elevation_data_result,
        "rainfall_data": rainfall_data_result
    }
    return result

# Example Easting and Northing for testing
easting = 159270
northing = 195374

# Fetch combined data
combined_data = get_combined_data(easting, northing)

# Print the results
print("Combined Data:")
print(combined_data)
