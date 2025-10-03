# from ensurepip import bootstrap
from distutils.util import change_root
from ensurepip import bootstrap
from platform import node
from sqlite3 import Timestamp
from kafka3 import KafkaProducer
from opcua import Client
import json
import time

# Connect to the OPC UA server:
opcua_server_url = "opc.tcp://localhost:4840"
"""NodeId of the 'TimeseriesData' object: NumericNodeId(ns=2;i=1)
Path of the 'TimeseriesData' object: /Objects/TimeseriesData"""
client = Client(opcua_server_url)
client.connect()
# Create Kafka Producer
bootstrap_servers = ['localhost:9092', 'localhost:9093', 'localhost:9094']
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)


def read_object_values(client, variable_names):
    '''
    Read values from the OPC UA server and pass them to the Kafka producer
    '''
    try:

        # Read the values of the variables under the object node
        values = {}
        for variable_name in variable_names:
            try:
                variable_node = client.get_node(variable_name)
                values[variable_name] = variable_node.get_value()
            except Exception as e:
                print(f"Error reading variable '{variable_name}': {e}")

        return values

    except Exception as e:
        print(f"Error while reading object values: {e}")


new_key_mapping = {
    "ns=2;i=2": "Timestamp",
    "ns=2;i=3": "Humidity",
    "ns=2;i=4": "Pressure",
    "ns=2;i=5": "AccelX",
    "ns=2;i=6": "AccelY",
    "ns=2;i=7": "AccelZ",
    "ns=2;i=8": "GyroX",
    "ns=2;i=9": "GyroY",
    "ns=2;i=10": "GyroZ",
    "ns=2;i=11": "T",
    "ns=2;i=12": "Noise",
    "ns=2;i=13": "Light"

}
x = 0
changed_dict = {
    "Timestamp": 1678380030.6959295,
    "Humidity": 29,
    "Pressure": 99355,
    "AccelX": 34,
    "AccelY": 34,
    "AccelZ": -1004,
    "GyroX": 61,
    "GyroY": 366,
    "GyroZ": -61,
    "T": 21.421,
    "Noise": 0.001379,
    "Light": 60480
}
while x < 10:
    nodes_timeseries = ["ns=2;i=2", "ns=2;i=3", "ns=2;i=4", "ns=2;i=5", "ns=2;i=6", "ns=2;i=7",
                        "ns=2;i=8", "ns=2;i=9", "ns=2;i=10", "ns=2;i=11", "ns=2;i=12", "ns=2;i=13"]  # from timeseries object
    values = read_object_values(client, nodes_timeseries)

    for original_key, new_key in new_key_mapping.items():
        if original_key in values:
            changed_dict[new_key] = values[original_key]
    if changed_dict:
        print("Values from TimeseriesData object:")
        for map_key, value in changed_dict.items():
            print(f"{map_key}: {value}  ")
    time.sleep(5)
    json_string = json.dumps(changed_dict)
    producer.send('your_topic', value=json_string.encode('utf-8'))
    producer.flush()
    x = x+1

producer.close()
client.disconnect()

"""
if values:
        print("Values from TimeseriesData object:")
        for variable_name, value in values.items():
            print(f"{variable_name}: {value}")"""

"""timestamp_variable = node_timeseries.get_child("Timestamp")
humidity_variable = node_timeseries.get_child("Humidity")

timestamp_value = timestamp_variable.get_value()
humidity_value = humidity_variable.get_value()

print(f"Timestamp: {timestamp_value}")
print(f"Humidity: {humidity_value}")"""


"""for _ in range(100):
producer.send('test',b'Hello from the Python produer')
#print("hola")
time.sleep(5) """
