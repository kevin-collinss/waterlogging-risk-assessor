import rasterio
from pyproj import Transformer
import csv

# Input file and output CSV paths
input_path = 'data/45N015W_3S.ACE2'
output_csv_path = 'valid_irish_coords_irish_grid.csv'

# Define Ireland's WGS84 bounds (longitude and latitude)
LON_MIN, LON_MAX = -10.5, -5.5
LAT_MIN, LAT_MAX = 51.4, 55.5  

# Define transformer (WGS84 -> Irish Grid EPSG:29903)
transformer = Transformer.from_crs("EPSG:4326", "EPSG:29903", always_xy=True)

# Open raster file
with rasterio.open(input_path) as src:
    elevation_data = src.read(1)  # Elevation data
    bounds = src.bounds
    width = src.width
    height = src.height

    # Calculate resolution (assumes consistent resolution)
    lon_resolution = (bounds.right - bounds.left) / width
    lat_resolution = (bounds.top - bounds.bottom) / height

    print(f"Raster bounds in WGS84: {bounds}")
    print(f"Longitude resolution: {lon_resolution}, Latitude resolution: {lat_resolution}")

    # Open CSV to save valid Irish coordinates
    with open(output_csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Lon', 'Lat', 'IrishGrid_Easting', 'IrishGrid_Northing', 'Elevation'])

        for row in range(elevation_data.shape[0]):
            for col in range(elevation_data.shape[1]):
                # Calculate longitude and latitude
                lon = bounds.left + col * lon_resolution
                lat = bounds.top - row * lat_resolution

                # Skip points outside Ireland's longitude and latitude bounds
                if not (LON_MIN <= lon <= LON_MAX and LAT_MIN <= lat <= LAT_MAX):
                    continue

                # Transform to Irish Grid
                irish_grid_easting, irish_grid_northing = transformer.transform(lon, lat)
                elevation = elevation_data[row, col]

                # Skip invalid elevation values
                if elevation in [-500, -32768]:
                    continue

                # Write valid Irish points to the CSV
                csv_writer.writerow([lon, lat, irish_grid_easting, irish_grid_northing, elevation])

print(f"Valid Irish coordinates written to {output_csv_path}")
