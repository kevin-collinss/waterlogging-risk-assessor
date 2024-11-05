import pandas as pd

# Load the GridData CSV file
grid_data_path = 'C:/Github/02_College/FYP/AFFAMMS/data/rainfall_data.csv'  # Update with the actual path
rainfall_df = pd.read_csv(grid_data_path)

def find_grid_for_coordinate(easting, northing):
    # Round the coordinates to the nearest kilometer
    rounded_easting = round(easting, -3)
    rounded_northing = round(northing, -3)

    # Find the row in the DataFrame with the matching grid coordinates
    matching_row = rainfall_df[(rainfall_df['east'] == rounded_easting) & (rainfall_df['north'] == rounded_northing)]
    
    if not matching_row.empty:
        return matching_row.to_dict(orient='records')[0]
    else:
        print("No data found for the given coordinates.")
        return None

easting = 221653
northing = 240885 
grid_info = find_grid_for_coordinate(easting, northing)

if grid_info:
    print("Grid Data:", grid_info)