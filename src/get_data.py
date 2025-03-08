import psycopg2
from pyproj import Transformer
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

transformer = Transformer.from_crs("EPSG:29903", "EPSG:2157", always_xy=True)


def is_within_boundary(easting, northing):
    """Check if the given point is within the boundary in the GeoPackage."""
    try:
        # Transform coordinates from EPSG:29903 to EPSG:2157
        transformed_easting, transformed_northing = transformer.transform(easting, northing)

        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
        SELECT PROVINCE
        FROM provinces___gen_20m_2019
        WHERE ST_Contains(
            SHAPE,
            ST_SetSRID(ST_MakePoint(%s, %s), 2157)
        );
        """
        cursor.execute(query, (transformed_easting, transformed_northing))
        result = cursor.fetchone()

        if result:
            return True
        else:
            return False

    except Exception as e:
        print(f"Database error: {e}")
        return False

    finally:
        if conn:
            cursor.close()
            conn.close()


def query_database(table_name, easting, northing):
    """Query the database for the closest point in the specified table."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        if table_name == "soil_data":
            # Query for soil data using geometry
            query = f"""
            SELECT *
            FROM {table_name}
            ORDER BY ST_SetSRID(geometry, 29903) <-> ST_SetSRID(ST_MakePoint(%s, %s), 29903)
            LIMIT 1;
            """
        elif table_name == "hydrology_data":
            # Query for hydrology data using geometry
            query = f"""
            SELECT *
            FROM {table_name}
            ORDER BY ST_SetSRID(geometry, 29903) <-> ST_SetSRID(ST_MakePoint(%s, %s), 29903)
            LIMIT 1;
            """
        elif table_name == "elevation_data":
            # Query for elevation data using easting and northing
            query = f"""
            SELECT easting, northing, elevation
            FROM {table_name}
            ORDER BY
                (POWER(easting - %s, 2) + POWER(northing - %s, 2))
            LIMIT 1;
            """
        elif table_name == "rainfall_data":
            # Query for rainfall data using easting and northing
            query = f"""
            SELECT easting, northing, ann, djf, mam, jja, son
            FROM {table_name}
            ORDER BY
                (POWER(easting - %s, 2) + POWER(northing - %s, 2))
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
        elif table_name == "elevation_data":
            return {
                "Easting": result[0],
                "Northing": result[1],
                "Elevation": result[2],
            }
        elif table_name == "rainfall_data":
            return {
                "Easting": result[0],
                "Northing": result[1],
                "ANN": result[2],
                "DJF": result[3],
                "MAM": result[4],
                "JJA": result[5],
                "SON": result[6],
            }

    except Exception as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()


def get_combined_data(easting, northing):
    # Check if the point is within the boundary
    province = is_within_boundary(easting, northing)
    if not province:
        return {"error": "Point is outside the defined boundary"}

    # Query soil and hydrology data from the database
    soil_data = query_database("soil_data", easting, northing)
    hydrology_data = query_database("hydrology_data", easting, northing)

    # Query elevation data from the database
    elevation_data = query_database("elevation_data", easting, northing)

    # Query rainfall data from the database
    rainfall_data = query_database("rainfall_data", easting, northing)

    # Combine results
    result = {
        "boundary_province": province,
        "soil_data": soil_data,
        "hydrology_data": hydrology_data,
        "elevation_data": elevation_data,
        "rainfall_data": rainfall_data,
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
