from database.engine import engine
from database.entities.timeseries import timeseries_table
from kafka3 import KafkaConsumer
import time
import json
import pprint
from sqlalchemy import exc, insert
from uuid import uuid4
import os
import sys
import datetime

# Helps to import from parent directory
# import sys
# ys.path.insert(0, '..')
sys.path.append(
    "D:/Tucloud/Shared/Entwicklung von der Daten-Streaming-Infrastruktur im KI-Labor/05 Software/OPC UA/daten-streaming-infrastruktur/")

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))


pp = pprint.PrettyPrinter(indent=4)

while True:
    print("Waiting for message...")
    consumer = KafkaConsumer(
        'TimeseriesData',
        bootstrap_servers=['host.internal.docker:9092',
                           'host.internal.docker:9093', 'host.internal.docker:9094'],
        group_id='test-consumer-group',
    )
    for message in consumer:
        pp.pprint(message)
        values = json.loads(message.value)
        pp.pprint(json.loads(message.value))

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
        )

        print(insert_query)

        try:
            with engine.connect() as conn:
                result = conn.execute(insert_query)
                pp.pprint(result)
                conn.commit()
        # except exc.SQLAlchemyError as e:  # parent of IOError, OSError *and* WindowsError where available
        #     print(e)
        except exc.DBAPIError as e:
            print(e)"""

    time.sleep(5)
