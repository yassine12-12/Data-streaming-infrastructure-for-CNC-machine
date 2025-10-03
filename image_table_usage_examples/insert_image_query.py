import psycopg2
from datetime import datetime
import os

# Database connection parameters
db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

# README: Change this to insert another image
# TIFF image file path
# image_path = 'demo_data/image_cnc/Basler_a2A1920-160ucPRO__40287467__20230313_145452597_0144.tiff'
directory = "./demo_data/image_cnc"

# Connect to the PostgreSQL database
# List all files in the directory

file_list = os.listdir(directory)

print('file_list', file_list)
# Loop through each file
for filename in file_list:
    # Check if the item is a file (not a directory)
    if not os.path.isfile(os.path.join(directory, filename)):
        continue

    if not filename.startswith('Basler'):
        continue

    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        image_path = "demo_data/image_cnc/{}".format(filename)

        print('image_path', image_path)
        # Read the image data from the file
        with open(image_path, 'rb') as file:
            file_data = file.read()

        # Extract information from the filename
        filename = os.path.basename(image_path)
        parts = filename.split('_')
        sensor_name = parts[0]
        # Combine year, month, day, and timestamp
        timestamp_str = '_'.join(parts[4:7])
        print('timestamp_str', timestamp_str)
        timestamp = datetime.strptime(timestamp_str, '_%Y%m%d_%H%M%S%f')

        # Insert the data into the 'images' table
        insert_query = """
        INSERT INTO images (sensor_name, timestamp, filename, file_data, dimension_1, dimension_2)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (sensor_name,
                                      timestamp, filename, file_data, 0, 0))
        conn.commit()

        print("Data inserted successfully.")

    except psycopg2.Error as e:
        print("Error:", e)

    finally:
        if conn is not None:
            conn.close()
