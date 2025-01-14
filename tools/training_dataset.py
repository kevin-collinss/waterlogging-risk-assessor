import json
import csv
import requests
import random

# Define bounds for Easting and Northing (Ireland)
EASTING_MIN = 13098
EASTING_MAX = 367154
NORTHING_MIN = 11478
NORTHING_MAX = 462251

# Output file for the dataset
output_csv = "training_data.csv"

# Define the number of valid data points to extract
num_points = 10000

# Features to extract (including Easting and Northing)
fields = ["Easting", "Northing", "Texture", "Description", "Elevation", "Annual_Rainfall", "Hydrology_Category"]

# Initialize CSV file
with open(output_csv, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(fields)  # Write the header

    valid_points = 0  # Counter for valid data points

    while valid_points < num_points:
        # Randomly generate a coordinate within the bounds
        easting = round(random.uniform(EASTING_MIN, EASTING_MAX))
        northing = round(random.uniform(NORTHING_MIN, NORTHING_MAX))

        # Make a POST request to the backend
        response = requests.post(
            "http://localhost:5000/get_data",  # Update this URL as needed
            headers={"Content-Type": "application/json"},
            data=json.dumps({"easting": easting, "northing": northing}),
        )

        if response.status_code == 200:
            try:
                # Parse the response
                data = response.json()

                # Check if all relevant data exists
                if (
                    not data["soil_data"].get("TEXTURE") or
                    not data["soil_data"].get("PlainEngli") or
                    not data["elevation_data"].get("Elevation") or
                    not data["rainfall_data"].get("ANN") or
                    not data["hydrology_data"].get("CATEGORY")
                ):
                    print(f"Skipped incomplete or out-of-bounds data at Easting: {easting}, Northing: {northing}")
                    continue

                # Extract the required fields
                texture = data["soil_data"].get("TEXTURE", "N/A")
                description = data["soil_data"].get("PlainEngli", "N/A")
                elevation = data["elevation_data"].get("Elevation", "N/A")
                annual_rainfall = data["rainfall_data"].get("ANN", "N/A")
                hydrology_category = data["hydrology_data"].get("CATEGORY", "N/A")

                # Write the data to the CSV (including Easting and Northing)
                writer.writerow([easting, northing, texture, description, elevation, annual_rainfall, hydrology_category])

                valid_points += 1  # Increment the counter for valid points
                print(f"Valid point added: {valid_points}/{num_points}")

            except Exception as e:
                print(f"Error processing response for Easting: {easting}, Northing: {northing} - {e}")
        else:
            print(f"Failed request for Easting: {easting}, Northing: {northing} - Status Code: {response.status_code}")

print(f"Data extraction complete. Saved {num_points} valid entries to {output_csv}.")
