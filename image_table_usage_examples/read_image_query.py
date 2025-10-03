import psycopg2
from datetime import datetime
from PIL import Image
import io

# Database connection parameters
db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

# Output directory for saving the fetched image
output_directory = 'output/'

# Connect to the PostgreSQL database
try:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Retrieve the image data from the database
    # Replace with the appropriate condition
    select_query = "SELECT file_data FROM images LIMIT 1"
    cursor.execute(select_query)  # Replace with the actual image ID
    file_data = cursor.fetchone()[0]

    # Convert the byte data to an image using PIL
    image = Image.open(io.BytesIO(file_data))

    # Plot the image
    image.show()

except psycopg2.Error as e:
    print("Error:", e)

finally:
    if conn is not None:
        conn.close()
