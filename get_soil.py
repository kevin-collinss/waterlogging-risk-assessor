import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, shape

# Load the CSV file
csv_path = 'C:/Github/02_College/FYP/AFFAMMS/data/soil_data.csv'
df = pd.read_csv(csv_path)

# Example coordinates to check
input_x = 221653  # Replace with your X coordinate
input_y = 240885  # Replace with your Y coordinate
point = Point(input_x, input_y)

# Iterate over the rows to check if the point is inside any polygon
soil_type = None
for index, row in df.iterrows():
    # Convert the WKT string to a shapely Polygon object
    polygon = shape(gpd.GeoSeries.from_wkt([row['geometry']])[0])

    # Check if the point is within the polygon
    if polygon.contains(point):
        soil_type = row['TEXTURE']  # Replace 'soil_type_column' with the actual column name for soil type
        break

if soil_type:
    print(f"The soil type at the given coordinates is: {soil_type}")
else:
    print("No soil type found for the given coordinates.")
