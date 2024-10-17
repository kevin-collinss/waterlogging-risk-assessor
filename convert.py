import geopandas as gpd

# Load the shapefile
shapefile_path = 'C:/Github/02_College/FYP/NationalSoilsHydrologyMap/NationalSoilsHydrologyMap.shp'
gdf = gpd.read_file(shapefile_path)

# Save as a CSV file
csv_output_path = 'C:/Github/02_College/FYP/AFFAMMS/data/hydrology_data.csv'
gdf.to_csv(csv_output_path, index=False)
