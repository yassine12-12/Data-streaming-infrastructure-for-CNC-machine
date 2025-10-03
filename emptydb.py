import psycopg2

# Database connection parameters
conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port=5432
)
cur = conn.cursor()

# Execute the DELETE statement
cur.execute("DELETE FROM public.processed_images")
cur.execute("DELETE FROM public.imagesraw")
cur.execute("DELETE FROM public.images")
cur.execute("DELETE FROM public.timeseriesraw")
cur.execute("DELETE FROM public.timeseries")
cur.execute("DELETE FROM public.processed_timeseries")


# Check how many rows were affected
deleted_rows = cur.rowcount
print(f"Deleted {deleted_rows} rows from public.processed_images")

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
