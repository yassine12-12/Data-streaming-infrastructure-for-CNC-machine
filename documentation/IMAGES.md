# Handling images

In order to test inserting and reading images some scripts were created inside `image_table_usage_example`

### To insert an image

The following script will insert the imagine located at `image_path = 'demo_data/image_cnc/Basler_a2A1920-160ucPRO__40287467__20230313_145452597_0145.tiff'`

```
python image_table_usage_examples/insert_image_query.py
```

In order to insert a different image change the `image_path` variable. Every image can be inserted only once or you will get a unique primary key error

### To print an image

The following query will fetch the first image found in the database and print it

```
python image_table_usage_examples/read_image_query.py
```
