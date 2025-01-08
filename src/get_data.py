import sys
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely import wkt

# Load the data files
soil_data = pd.read_csv("data/soil_data.csv")
hydrology_data = pd.read_csv("data/hydrology_data.csv")
elevation_data = pd.read_csv("data/elevation_data.csv")
rainfall_data = pd.read_csv("data/rainfall_data.csv")

# Parse geometry columns in soil and hydrology data
soil_data['geometry'] = soil_data['geometry'].apply(wkt.loads)
hydrology_data['geometry'] = hydrology_data['geometry'].apply(wkt.loads)

# Convert to GeoDataFrames
soil_gdf = gpd.GeoDataFrame(soil_data, geometry=soil_data['geometry'])
hydrology_gdf = gpd.GeoDataFrame(hydrology_data, geometry=hydrology_data['geometry'])

# Ensure elevation and rainfall data have no extra spaces in column names
elevation_data.rename(columns=lambda x: x.strip(), inplace=True)
rainfall_data.rename(columns=lambda x: x.strip(), inplace=True)

# Ensure required columns exist
required_elevation_columns = ['Easting', 'Northing', 'Elevation']
required_rainfall_columns = ['Easting', 'Northing', 'ANN', 'DJF', 'MAM', 'JJA', 'SON']

for col in required_elevation_columns:
    if col not in elevation_data.columns:
        raise ValueError(f"Missing required column: {col} in elevation_data.csv")

for col in required_rainfall_columns:
    if col not in rainfall_data.columns:
        raise ValueError(f"Missing required column: {col} in rainfall_data.csv")


def get_combined_data(easting, northing):
    point = Point(easting, northing)
    point_gdf = gpd.GeoDataFrame(index=[0], geometry=[point], crs=soil_gdf.crs)

    soil_result = gpd.sjoin(point_gdf, soil_gdf, how="inner", predicate='intersects')
    hydrology_result = gpd.sjoin(point_gdf, hydrology_gdf, how="inner", predicate='intersects')

    elevation_data['Distance'] = ((elevation_data['Easting'] - easting) ** 2 + (elevation_data['Northing'] - northing) ** 2).pow(0.5)
    closest_elevation = elevation_data.loc[elevation_data['Distance'].idxmin()]

    rainfall_data['Distance'] = ((rainfall_data['Easting'] - easting) ** 2 + (rainfall_data['Northing'] - northing) ** 2).pow(0.5)
    closest_rainfall = rainfall_data.loc[rainfall_data['Distance'].idxmin()]

    result = {
        "soil_data": {
            "POINT": str(soil_result.geometry.iloc[0]) if not soil_result.empty else None,
            "Texture_Su": soil_result["Texture_Su"].iloc[0] if not soil_result.empty else None,
            "TEXTURE": soil_result["TEXTURE"].iloc[0] if not soil_result.empty and pd.notna(soil_result["TEXTURE"].iloc[0]) else None,
            "DEPTH": soil_result["DEPTH"].iloc[0] if not soil_result.empty and pd.notna(soil_result["DEPTH"].iloc[0]) else None,
            "PlainEngli": soil_result["PlainEngli"].iloc[0] if not soil_result.empty else None,
        },
        "hydrology_data": {
            "CATEGORY": hydrology_result["CATEGORY"].iloc[0] if not hydrology_result.empty else None,
            "ParMat_Des": hydrology_result["ParMat_Des"].iloc[0] if not hydrology_result.empty else None,
            "SoilDraina": hydrology_result["SoilDraina"].iloc[0] if not hydrology_result.empty else None,
        },
        "elevation_data": {
            "Elevation": closest_elevation["Elevation"]
        },
        "rainfall_data": {
            "ANN": closest_rainfall["ANN"],
            "DJF": closest_rainfall["DJF"],
            "MAM": closest_rainfall["MAM"],
            "JJA": closest_rainfall["JJA"],
            "SON": closest_rainfall["SON"]
        }
    }
    return result


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(json.dumps({"error": "Provide easting and northing as arguments"}))
        sys.exit(1)

    try:
        easting = float(sys.argv[1])
        northing = float(sys.argv[2])

        data = get_combined_data(easting, northing)
        print(json.dumps(data))  # Output result as JSON

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
