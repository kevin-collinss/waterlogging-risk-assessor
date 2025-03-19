import psycopg2
from pyproj import Transformer
import json
import sys
import joblib

# Initialize debug log list
debug_logs = []

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
    conn = None
    try:
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
        return True if result else False
    except Exception as e:
        debug_logs.append(f"Database error in is_within_boundary: {e}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

def query_database(table_name, easting, northing):
    """Query the database for the closest point in the specified table."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        if table_name == "soil_data":
            query = f"""
            SELECT *
            FROM {table_name}
            ORDER BY ST_SetSRID(geometry, 29903) <-> ST_SetSRID(ST_MakePoint(%s, %s), 29903)
            LIMIT 1;
            """
        elif table_name == "hydrology_data":
            query = f"""
            SELECT *
            FROM {table_name}
            ORDER BY ST_SetSRID(geometry, 29903) <-> ST_SetSRID(ST_MakePoint(%s, %s), 29903)
            LIMIT 1;
            """
        elif table_name == "elevation_data":
            query = f"""
            SELECT easting, northing, elevation
            FROM {table_name}
            ORDER BY
                (POWER(easting - %s, 2) + POWER(northing - %s, 2))
            LIMIT 1;
            """
        elif table_name == "rainfall_data":
            query = f"""
            SELECT easting, northing, ann, djf, mam, jja, son
            FROM {table_name}
            ORDER BY
                (POWER(easting - %s, 2) + POWER(northing - %s, 2))
            LIMIT 1;
            """
        else:
            return None
        cursor.execute(query, (easting, northing))
        result = cursor.fetchone()
        if not result:
            return None
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
        debug_logs.append(f"Database error in query_database for {table_name}: {e}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_combined_data(easting, northing):
    province = is_within_boundary(easting, northing)
    if not province:
        return {"error": "Point is outside the defined boundary"}
    soil_data = query_database("soil_data", easting, northing)
    hydrology_data = query_database("hydrology_data", easting, northing)
    elevation_data = query_database("elevation_data", easting, northing)
    rainfall_data = query_database("rainfall_data", easting, northing)
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
        output = {"error": "Provide easting and northing as arguments", "debug": debug_logs}
        print(json.dumps(output))
        sys.exit(1)
    try:
        easting = float(sys.argv[1])
        northing = float(sys.argv[2])
        data = get_combined_data(easting, northing)
        debug_logs.append("DEBUG: Entire data dictionary:\n" + json.dumps(data, indent=2))
        if "error" not in data:
            try:
                # Use TEXTURE if present; if not, fallback to Texture_Su.
                let_texture = data.get("soil_data", {}).get("TEXTURE")
                if not let_texture:
                    let_texture = data.get("soil_data", {}).get("Texture_Su")
                texture = let_texture
                elevation = data.get("elevation_data", {}).get("Elevation")
                annual_rainfall = data.get("rainfall_data", {}).get("ANN")
                hydrology_category = data.get("hydrology_data", {}).get("CATEGORY")
                debug_logs.append(f"DEBUG: texture = {texture}")
                debug_logs.append(f"DEBUG: elevation = {elevation}")
                debug_logs.append(f"DEBUG: annual_rainfall = {annual_rainfall}")
                debug_logs.append(f"DEBUG: hydrology_category = {hydrology_category}")
                if None not in (texture, elevation, annual_rainfall, hydrology_category):
                    try:
                        elevation = float(elevation)
                        annual_rainfall = float(annual_rainfall)
                    except ValueError as ve:
                        debug_logs.append("DEBUG: Error converting numeric fields: " + str(ve))
                        data["cluster_prediction_error"] = "Missing one or more required feature values"
                    else:
                        texture_encoder = joblib.load("./models/texture_encoder.pkl")
                        hydrology_encoder = joblib.load("./models/hydrology_encoder.pkl")
                        scaler = joblib.load("./models/scaler.pkl")
                        classifier = joblib.load("./models/best_cluster_classifier.pkl")
                        texture_encoded = texture_encoder.transform([texture])[0]
                        hydrology_encoded = hydrology_encoder.transform([hydrology_category])[0]
                        feature_vector = [texture_encoded, elevation, annual_rainfall, hydrology_encoded]
                        feature_vector_scaled = scaler.transform([feature_vector])
                        predicted_cluster = classifier.predict(feature_vector_scaled)[0]
                        debug_logs.append(f"DEBUG: Successfully predicted cluster: {predicted_cluster}")
                        data["cluster_prediction"] = int(predicted_cluster)
                else:
                    debug_logs.append("DEBUG: One or more fields is missing from the data.")
                    data["cluster_prediction_error"] = "Missing one or more required feature values"
            except Exception as e:
                debug_logs.append("DEBUG: Exception during cluster prediction: " + str(e))
                data["cluster_prediction_error"] = str(e)
        # Only add debug logs to output if there's an error
        if "cluster_prediction_error" in data:
            data["debug"] = debug_logs
        print(json.dumps(data))
    except Exception as e:
        print(json.dumps({"error": str(e), "debug": debug_logs}))
        sys.exit(1)
