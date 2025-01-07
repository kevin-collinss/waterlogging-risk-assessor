import csv

# Path to your CSV file
csv_file_path = 'data/elevation_data.csv'

# Read the first line
with open(csv_file_path, 'r') as file:
    reader = csv.reader(file)
    first_line = next(reader)  # Get the first line
    print(first_line)
