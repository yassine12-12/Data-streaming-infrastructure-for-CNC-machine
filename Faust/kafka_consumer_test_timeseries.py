#from database.engine import engine
#from database.entities.timeseries import timeseries_table
from kafka3 import KafkaConsumer
from confluent_kafka import Consumer,KafkaError, KafkaException
import psycopg2
from psycopg2 import extras
import time
import json
import pprint
import yaml
#from sqlalchemy import exc, insert
#from uuid import uuid4
import os
import sys
from datetime import datetime
# Helps to import from parent directory
# import sys
# ys.path.insert(0, '..')
#sys.path.append(
#    "D:/Tucloud/Shared/Entwicklung von der Daten-Streaming-Infrastruktur im KI-Labor/05 Software/OPC UA/daten-streaming-infrastruktur/")

#sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def read_config(path):
    """
    Read configuration settings from a YAML file named 'config.yml'.

    Returns:
        dict: A dictionary containing the configuration settings.

    Note:
        - If the file is successfully parsed, the settings are returned as a dictionary.
        - If any YAML parsing error occurs, the exception is printed, and the function returns None.
    """
    with open(path, "r") as ymlfile:
        try:
            cfg = yaml.full_load(ymlfile)
            return cfg
        except yaml.YAMLError as exc:
            print(exc)
config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yml")
cfg = read_config(config_file_path) 

conn = psycopg2.connect(
    database=cfg["postgres"]["database"],
    user=cfg["postgres"]["user"],
    password=cfg["postgres"]["password"],
    host=cfg["postgres"]["host"],
    port=cfg["postgres"]["port"]
)
cursor = conn.cursor()
pp = pprint.PrettyPrinter(indent=4)

consumer_conf = {
        'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
        'group.id': 'timeseries',
        'auto.offset.reset': 'earliest'  # Start reading from the beginning of the topic if no offset is stored
    }
consumer = Consumer(consumer_conf)
consumer.subscribe(["sink_topic"])
    
while True:
    print("Waiting for message...")
    
    msg = consumer.poll()
    if msg is None:
        continue
    try:
        # Decode the message value assuming it's in utf-8 encoding
        message_value = msg.value().decode('utf-8')
        msg_value_dict = json.loads(message_value)
        msg_value_dict["sensor_name"] = "TimeseriesTest"
        timestamp_value = datetime.fromtimestamp(msg_value_dict["start_time"])

        msg_value_dict['timestamp'] = timestamp_value
        #print("Received JSON data:")
        pp.pprint(message_value)
        print(msg_value_dict)
        insert_query = """INSERT INTO timeseries 
        (sensor_name, timestamp, humidity, pressure, acceleration_x, acceleration_y, acceleration_z, gyro_x, gyro_y, gyro_z, temperature, noise, light) 
        VALUES (%(sensor_name)s,%(timestamp)s, %(Humidity)s, %(Pressure)s, %(AccelX)s, %(AccelY)s, %(AccelZ)s, %(GyroX)s, %(GyroY)s, %(GyroZ)s, %(T)s, %(Noise)s, %(Light)s)"""
        cursor.execute(insert_query, msg_value_dict) #decirle a adrian si el timestamp de la base de datos la podemos guardar como numerico para que asi cada quien lo pueda leer como quiera 
        # Commit the transaction
        conn.commit()

    except Exception as e:
        print(f"Error processing message: {e}")
        cursor.close()
        conn.close()
cursor.close()
conn.close()





    