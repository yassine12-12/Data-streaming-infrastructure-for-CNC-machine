from datetime import datetime, timedelta, date
from time import time
import random
import faust
import numpy as np
from lstm_autoencoder import RecurrentAutoencoder
import seaborn as sns
import pandas as pd

# Befehlt zum Aufruf der Anwendung
# py -m pipenv run faust -A faust_test_timeseries worker -l info


# Definition der Struktur der ankommenden Daten
class RawModel(faust.Record):
    Timestamp: datetime
    Humidity : float
    Pressure : float
    AccelX : float
    AccelY : float
    AccelZ : float
    GyroX : float
    GyroY : float
    GyroZ : float
    T : float
    Noise : float
    Light : float

class IntList(faust.Record, serializer='json'):
    data: list[dict[str, float]]

# Definition der output Datenstruktur
class AggModel_mean(faust.Record):
    date: datetime
    start_time : datetime
    end_time : datetime
    Humidity : float
    Pressure : float
    AccelX : float
    AccelY : float
    AccelZ : float
    GyroX : float
    GyroY : float
    GyroZ : float
    T : float
    Noise : float
    Light : float
    count: int

KAFKA = ['kafka://localhost:9092',"kafka://localhost:9093","kafka://localhost:9094"]
# Definition grundlegender Parameter
TOPIC = 'TimeseriesData'
SINK = 'faust_sink_timeseries_AI'
TABLE = 'tumbling_table_AI'
KAFKA = KAFKA
CLEANUP_INTERVAL = 10.0     #Zeit nach der gebufferte Daten gelöscht werden 
WINDOW = 3  # Fenster Länge
WINDOW_EXPIRES = 10
PARTITIONS = 1  # Menge an Partitionen

app = faust.App('windowed-agg', broker=KAFKA, version=1, topic_partitions=1)

app.conf.table_cleanup_interval = CLEANUP_INTERVAL
source = app.topic(TOPIC, value_type = RawModel) #, value_type=list
sink = app.topic(SINK, value_type=AggModel_mean)


def window_processor(key, events):
    # Funktion zur Berechnun des Durchschnitts 
    def mean(value,count):
        return sum(value) / count

    for event in events: 
        print("printing event type",type(event))
    timestamps = [event.Timestamp for event in events]
    # einlesen der Fenster Daten
    humidities = [event.Humidity for event in events]
    pressures = [event.Pressure for event in events]
    accelXes = [event.AccelX for event in events]
    accelYes = [event.AccelY for event in events]
    accelZes = [event.AccelZ for event in events]
    gyroXes = [event.GyroX for event in events]
    gyroYes = [event.GyroY for event in events]
    gyroZes = [event.GyroZ for event in events]
    tes = [event.T for event in events]
    noises = [event.Noise for event in events]
    lights = [event.Light for event in events]
    count = len(timestamps)
    

    sink.send_soon(value=AggModel_mean(date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),start_time = timestamps[0],end_time = timestamps[-1],
                                  Humidity = mean(humidities,count),Pressure=mean(pressures,count),AccelX=mean(accelXes,count),
                                  AccelY=mean(accelYes,count),AccelZ=mean(accelZes,count),GyroX=mean(gyroXes,count),GyroY=mean(gyroYes,count),
                                  GyroZ=mean(gyroZes,count),T=mean(tes,count),Noise=mean(noises,count),Light=mean(lights,count), count=count))

# Definition der Tumbling Table einstellungen
tumbling_table = (
    app.Table(
        TABLE,
        default=list,
        partitions=PARTITIONS,
        on_window_close=window_processor, # Bearbeitungsfunktion
    )
    .tumbling(WINDOW, expires=timedelta(seconds=WINDOW_EXPIRES))
    .relative_to_field(RawModel.Timestamp)
)


model = RecurrentAutoencoder()
path_model = ".\model_noise.pth" # trainierte model ausrufen
THRESHOLD = 0.1

@app.agent(source)
async def print_windowed_events(stream):
    async for event in stream:

        my_array = np.array([[event.Noise]])  # Creating a 2D array with one row and one column
        # make prediction
        predictions, pred_losses = model.predict(path_model, my_array)
        sns.distplot(pred_losses, bins=50, kde=True)
        correct = sum(l <= THRESHOLD for l in pred_losses)

        print(event.Noise)
        print("---------")
        event.Noise= float(predictions[0]) #save prediction in event  noise 
        print(event.Noise)

        value_list = tumbling_table['events'].value()
        value_list.append(event)
        tumbling_table['events'] = value_list

if __name__ == '__main__':
    app.main()