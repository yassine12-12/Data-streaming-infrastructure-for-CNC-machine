import psycopg2
from datetime import datetime
import os
import yaml
from psycopg2 import extras

from OPCUA.json_merger import merge_json_files

config_file_path = os.path.join(os.getcwd(), "./config.yml")
with open(config_file_path, "r") as ymlfile:
    try:
        cfg = yaml.full_load(ymlfile)
    except yaml.YAMLError as exc:
        print(exc)


conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port=5432
)

path_1 = cfg["opcua"]["timeseries1"]
path_2 = cfg["opcua"]["timeseries2"]
path_3 = cfg["opcua"]["timeseries3"]

sensor_1_data = merge_json_files([path_1])
sensor_2_data = merge_json_files([path_2])
sensor_3_data = merge_json_files([path_3])

# Create a cursor with named tuples
cursor = conn.cursor(cursor_factory=extras.NamedTupleCursor)


def prepare_sensor_data(sensor_name, data):
    return [(sensor_name, datetime.fromtimestamp(d["timestamp"]), d["Humidity"], d["Pressure"], d["AccelX"], d["AccelY"],
             d["AccelZ"], d["GyroX"], d["GyroY"], d["GyroZ"], d["T"], d["Noise"], d["Light"]) for d in data]


insert_query = """
    INSERT INTO timeseries
        (sensor_name, timestamp, humidity, pressure, acceleration_x, acceleration_y, acceleration_z, gyro_x, gyro_y, gyro_z, temperature, noise, light) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""


prepared_sensor_1 = prepare_sensor_data("sensor_1", sensor_1_data)
prepared_sensor_2 = prepare_sensor_data("sensor_2", sensor_2_data)
prepared_sensor_3 = prepare_sensor_data("sensor_3", sensor_3_data)


try:
    # Execute the batch insert
    extras.execute_batch(cursor, insert_query, prepared_sensor_1)
    extras.execute_batch(cursor, insert_query, prepared_sensor_2)
    extras.execute_batch(cursor, insert_query, prepared_sensor_3)

    conn.commit()
except Exception as error:
    print(error)


conn.close()
