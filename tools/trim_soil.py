import pandas as pd
from shapely import wkt

# Load the dataset
soil_data = pd.read_csv("data/soil_data_full.csv")

# Parse geometry column
soil_data['geometry'] = soil_data['geometry'].apply(wkt.loads)

# Add bounding box columns for spatial filtering
soil_data['min_x'] = soil_data['geometry'].apply(lambda geom: geom.bounds[0])
soil_data['min_y'] = soil_data['geometry'].apply(lambda geom: geom.bounds[1])
soil_data['max_x'] = soil_data['geometry'].apply(lambda geom: geom.bounds[2])
soil_data['max_y'] = soil_data['geometry'].apply(lambda geom: geom.bounds[3])

# Define a grid size (in meters) for clustering
grid_size = 1000  # 1 km grid

# Assign grid IDs for clustering
soil_data['grid_id'] = (
    (soil_data['min_x'] // grid_size).astype(int).astype(str) + "_" +
    (soil_data['min_y'] // grid_size).astype(int).astype(str)
)

# Save the optimised dataset with bounding boxes and grid IDs
soil_data[[
    "min_x", "min_y", "max_x", "max_y", "grid_id",
    "Texture_Su", "TEXTURE", "DEPTH", "PlainEngli"
]].to_csv("soil_data_optimised.csv", index=False)

print("Optimisation complete. Data saved to soil_data_optimised.csv.")
