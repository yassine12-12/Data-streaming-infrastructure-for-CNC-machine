from kafka3 import KafkaConsumer
import time
import json
import pprint
from sqlalchemy import exc, insert
from uuid import uuid4
import psycopg2
import os
import sys
import datetime
from confluent_kafka import Consumer,KafkaError, KafkaException

# Helps to import from parent directory
# import sys
#ys.path.insert(0, '..')
#sys.path.append("/home/jan/Documents/AutPrj/daten-streaming-infrastruktur/")

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#from database.entities.image import images_table
#from database.engine import engine

conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port=5432
)
cursor = conn.cursor()

consumer_conf = {
        'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
        'group.id': 'ImageDatafaust',
        'auto.offset.reset': 'earliest'  # Start reading from the beginning of the topic if no offset is stored
    }
pp = pprint.PrettyPrinter(indent=4)
consumer = Consumer(consumer_conf)
consumer.subscribe(['faust_sink_image']) #topic name from where i want to read
while True:
    print("Waiting for message...")
    msg = consumer.poll() # i get the records 

    if msg is None:
        continue
    try:
        # Decode the message value assuming it's in utf-8 encoding
        message_value = msg.value().decode('utf-8') #deseralization of the data
        msg_value_dict = json.loads(message_value) #umwandlung zu dictionary
        msg_value_dict["Timestamp"] =  datetime.datetime.now() #create timestamp for the insertion
        msg_value_dict["dimension_2"]= 0 #create value so we can do the insert do we need it how do we get it from the shape
        msg_value_dict["dimension_1"] = int(''.join(map(str,msg_value_dict["shape"] ))) # shape is a list, so for interting it i change it to a integer 
        msg_value_dict["bytea"] = bytearray(msg_value_dict["ImageBlob"]) # imageblob is an array and for interting into the database it should be a bytea 
        msg_value_dict["filename"] = msg_value_dict["ImageSensor"] # the database ask for a file name, i create this file name for the insert
        print(type(msg_value_dict["ImageBlob"])) 
        insert_query = """INSERT INTO images
        (sensor_name, timestamp, file_data,dimension_1,dimension_2,filename)  
        VALUES (%(ImageSensor)s,%(Timestamp)s, %(bytea)s,%(dimension_1)s,%(dimension_2)s,%(filename)s)""" # the red ones are the database columnsname the blue theyare the keys of the msg_value_dict !!!
        cursor.execute(insert_query, msg_value_dict) # hier i execute the insert 
        conn.commit()
    except Exception as e:
        print(f"Error processing message: {e}")
        cursor.close()
        conn.close()
       
cursor.close()
conn.close()