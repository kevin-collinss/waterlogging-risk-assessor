import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely import wkt

# Load the soil data and hydrology data CSVs
soil_data = pd.read_csv("data/soil_data.csv")
hydrology_data = pd.read_csv("data/hydrology_data.csv")

# Ensure the geometry column is properly parsed as shapely geometries
soil_data['geometry'] = soil_data['geometry'].apply(wkt.loads)
hydrology_data['geometry'] = hydrology_data['geometry'].apply(wkt.loads)

# Convert DataFrames to GeoDataFrames
soil_gdf = gpd.GeoDataFrame(soil_data, geometry=soil_data['geometry'])
hydrology_gdf = gpd.GeoDataFrame(hydrology_data, geometry=hydrology_data['geometry'])

# Define the coordinates you want to query
longitude, latitude = 159270, 195374
point = Point(longitude, latitude)

# Create a GeoDataFrame for the point
point_gdf = gpd.GeoDataFrame(index=[0], geometry=[point], crs=soil_gdf.crs)

# Perform a spatial join between the point and the soil dataset
soil_result = gpd.sjoin(point_gdf, soil_gdf, how="inner", predicate='intersects')
soil_filtered = soil_result[['geometry', 'PlainEngli', 'DEPTH']]  # Select desired columns

# Perform a spatial join between the point and the hydrology dataset
hydrology_result = gpd.sjoin(point_gdf, hydrology_gdf, how="inner", predicate='intersects')
hydrology_filtered = hydrology_result[['geometry', 'CATEGORY', 'ParMat_Des', 'SoilDraina']]  # Select desired columns

# Display the filtered results
print("Filtered Results from Soil Data:")
print(soil_filtered)

print("\nFiltered Results from Hydrology Dataset:")
print(hydrology_filtered)
