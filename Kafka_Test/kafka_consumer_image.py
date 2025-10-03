#from database.engine import engine
#from database.entities.timeseries import timeseries_table
from kafka3 import KafkaConsumer
from confluent_kafka import Consumer,KafkaError, KafkaException
import psycopg2
from psycopg2 import extras
import time
import json
import pprint
from sqlalchemy import exc, insert
from uuid import uuid4
import os
import sys
from datetime import datetime
# Helps to import from parent directory
# import sys
# ys.path.insert(0, '..')
#sys.path.append(
#    "D:/Tucloud/Shared/Entwicklung von der Daten-Streaming-Infrastruktur im KI-Labor/05 Software/OPC UA/daten-streaming-infrastruktur/")

#sys.path.append(os.path.dirname(os.path.abspath(__file__)))


conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port=5432
)
cursor = conn.cursor()
pp = pprint.PrettyPrinter(indent=4)
consumer_conf = {
        'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
        'group.id': 'TimeseriesData',
        'auto.offset.reset': 'earliest'  # Start reading from the beginning of the topic if no offset is stored
    }
consumer = Consumer(consumer_conf)
consumer.subscribe(['ImageData'])
    
while True:
    print("Waiting for message...")
    
    msg = consumer.poll()
    if msg is None:
        continue
    try:
        # Decode the message value assuming it's in utf-8 encoding
        message_value = msg.value().decode('utf-8')
        msg_value_dict = json.loads(message_value)
        timestamp_value = datetime.fromtimestamp(msg_value_dict['ImageTimestamp'])
        msg_value_dict['ImageBlobHex']=msg_value_dict["ImageBlob"].encode('utf-8').hex()
        #print("Received JSON data:")
        #pp.pprint(message_value)
        print(type(msg_value_dict["ImageBlobHex"]))
        insert_query = """INSERT INTO imagesraw
        (sensor_name, timestamp, file_data) 
        VALUES (%(ImageSensor)s,%(Image_Timestamp)s, %(ImageBlobHex)s)"""
        print(msg_value_dict)
        cursor.execute(insert_query, msg_value_dict) #decirle a adrian si el timestamp de la base de datos la podemos guardar como numerico para que asi cada quien lo pueda leer como quiera 
        # Commit the transaction
        conn.commit()

    except Exception as e:
        print(f"Error processing message: {e}")
        #cursor.close()





"""insert_query = insert(timeseries_table).values(
humidity=msg_value_dict['Humidity'],
acceleration_x=msg_value_dict['AccelX'],
acceleration_y=msg_value_dict['AccelY'],
acceleration_z=msg_value_dict['AccelZ'],
gyro_x=msg_value_dict['GyroX'],
gyro_y=msg_value_dict['GyroY'],
gyro_z=msg_value_dict['GyroZ'],
temperature=msg_value_dict['T'],
noise=msg_value_dict['Noise'],
light=msg_value_dict['Light']
)"""



"""insert_query = insert(timeseries_table).values(
    # TODOo: Add UUID4 for testing
    sensor_name='domenica_me_tiene_pasando_hambre_1',
    timestamp=datetime.datetime.fromtimestamp(values['Timestamp']),
    humidity=values['Humidity'],
    pressure=values['Pressure'],
    acceleration_x=values['AccelX'],
    acceleration_y=values['AccelY'],
    acceleration_z=values['AccelZ'],
    gyro_x=values['GyroX'],
    gyro_y=values['GyroY'],
    gyro_z=values['GyroZ'],
    temperature=values['T'],
    noise=values['Noise'],
    light=values['Light']
)"""



    