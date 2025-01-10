import psycopg2
import pandas as pd
import numpy as np
import json
import sys

# Database connection parameters
DB_CONFIG = {
    "dbname": "soil_data",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": 5432,
}

# Load elevation and rainfall data files
elevation_data = pd.read_csv("data/elevation_data.csv")
rainfall_data = pd.read_csv("data/rainfall_data.csv")

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


def query_database(table_name, easting, northing):
    """Query the database for the closest point in the specified table."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = f"""
        SELECT *
        FROM {table_name}
        ORDER BY ST_SetSRID(geometry, 29903) <-> ST_SetSRID(ST_MakePoint(%s, %s), 29903)
        LIMIT 1;
        """
        cursor.execute(query, (easting, northing))
        result = cursor.fetchone()

        if table_name == "soil_data":
            return {
                "Texture_Su": result[1],
                "TEXTURE": result[2],
                "DEPTH": result[3],
                "PlainEngli": result[4],
            }
        elif table_name == "hydrology_data":
            return {
                "CATEGORY": result[1],
                "ParMat_Des": result[2],
                "SoilDraina": result[3],
            }

    except Exception as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()


def get_combined_data(easting, northing):
    # Query soil and hydrology data from the database
    soil_data = query_database("soil_data", easting, northing)
    hydrology_data = query_database("hydrology_data", easting, northing)

    # Find the closest elevation data point
    elevation_data['Distance'] = np.sqrt((elevation_data['Easting'] - easting) ** 2 +
                                         (elevation_data['Northing'] - northing) ** 2)
    closest_elevation = elevation_data.loc[elevation_data['Distance'].idxmin()]

    # Find the closest rainfall data point
    rainfall_data['Distance'] = np.sqrt((rainfall_data['Easting'] - easting) ** 2 +
                                        (rainfall_data['Northing'] - northing) ** 2)
    closest_rainfall = rainfall_data.loc[rainfall_data['Distance'].idxmin()]

    # Combine results
    result = {
        "soil_data": soil_data,
        "hydrology_data": hydrology_data,
        "elevation_data": {
            "Easting": closest_elevation["Easting"],
            "Northing": closest_elevation["Northing"],
            "Elevation": closest_elevation["Elevation"]
        },
        "rainfall_data": {
            "Easting": closest_rainfall["Easting"],
            "Northing": closest_rainfall["Northing"],
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
