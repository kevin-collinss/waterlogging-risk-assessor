import rasterio
import csv

input_path = 'data/45N015W_LAND_30S.ACE2'  
output_csv_path = 'filtered_elevation_data.csv'  

with rasterio.open(input_path) as src:
   
    elevation_data = src.read(1)  
    
    # Get the metadata for coordinate transformation
    transform = src.transform

    with open(output_csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Easting', 'Northing', 'Elevation'])

        for row in range(elevation_data.shape[0]):
            for col in range(elevation_data.shape[1]):
                
                easting, northing = transform * (col, row)
                elevation = elevation_data[row, col]
                #skip rows that are -500(in the sea) or +367146 in the UK
                if elevation == -500 or easting >= 367146:
                    continue  
                
                csv_writer.writerow([easting, northing, elevation])

print(f"Filtered elevation data has been written to {output_csv_path}")
