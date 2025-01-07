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


def find_nearest(df, easting, northing):
    """Find the nearest point in a DataFrame based on Euclidean distance."""
    df['Distance'] = ((df['Easting'] - easting) ** 2 + (df['Northing'] - northing) ** 2).pow(0.5)
    return df.loc[df['Distance'].idxmin()]


def get_combined_data(easting, northing):
    point = Point(easting, northing)
    point_gdf = gpd.GeoDataFrame(index=[0], geometry=[point], crs=soil_gdf.crs)

    # Find the nearest soil data
    if not soil_gdf.empty:
        soil_gdf['Distance'] = soil_gdf.geometry.apply(lambda geom: geom.distance(point))
        nearest_soil = soil_gdf.loc[soil_gdf['Distance'].idxmin()]
    else:
        nearest_soil = None

    # Find the nearest hydrology data
    if not hydrology_gdf.empty:
        hydrology_gdf['Distance'] = hydrology_gdf.geometry.apply(lambda geom: geom.distance(point))
        nearest_hydrology = hydrology_gdf.loc[hydrology_gdf['Distance'].idxmin()]
    else:
        nearest_hydrology = None

    # Find the closest elevation data
    closest_elevation = find_nearest(elevation_data, easting, northing)

    # Find the closest rainfall data
    closest_rainfall = find_nearest(rainfall_data, easting, northing)

    # Prepare the result
    result = {
        "soil_data": {
            "POINT": str(nearest_soil.geometry) if nearest_soil is not None else None,
            "Texture_Su": nearest_soil["Texture_Su"] if nearest_soil is not None else None,
            "TEXTURE": nearest_soil["TEXTURE"] if nearest_soil is not None else None,
            "DEPTH": nearest_soil["DEPTH"] if nearest_soil is not None else None,
            "PlainEngli": nearest_soil["PlainEngli"] if nearest_soil is not None else None,
        },
        "hydrology_data": {
            "CATEGORY": nearest_hydrology["CATEGORY"] if nearest_hydrology is not None else None,
            "ParMat_Des": nearest_hydrology["ParMat_Des"] if nearest_hydrology is not None else None,
            "SoilDraina": nearest_hydrology["SoilDraina"] if nearest_hydrology is not None else None,
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
