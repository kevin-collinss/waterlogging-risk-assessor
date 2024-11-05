import geopandas as gpd
from shapely.geometry import Point

# Load soil data
soil_data = gpd.read_file("C:/Github/02_College/FYP/SOIL_SISNationalSoils_shp/Data/SOIL_SISNationalSoils.shp")
soil_quality = gpd.read_file("C:/Github/02_College/FYP/NationalSoilsHydrologyMap/NationalSoilsHydrologyMap.shp")

# Define the coordinates you want to query
longitude, latitude = 159270, 195374
point = Point(longitude, latitude)

# Create a GeoDataFrame for the point
point_gdf = gpd.GeoDataFrame(index=[0], geometry=[point], crs=soil_quality.crs)

# Perform a spatial join between the point and the first dataset
soil_result = gpd.sjoin(point_gdf, soil_data, how="inner", predicate='intersects')

# Perform a spatial join between the point and the second dataset
quality_result = gpd.sjoin(point_gdf, soil_quality, how="inner", predicate='intersects')

# Display the results from both joins
print("Results from soil data:")
print(soil_result)

print("\nResults from quality dataset:")
print(quality_result)
