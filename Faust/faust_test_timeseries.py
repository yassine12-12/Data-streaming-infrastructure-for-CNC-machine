from datetime import datetime, timedelta, date
from time import time
import random
import faust
# py -m pipenv run faust -A faust_test_timeseries worker -l info --web-port 6066
# meherere processe auf einmal starten 
# port ist immer gleich  = socket
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


TOPIC = 'TimeseriesData' #reading from this topic
SINK = 'sink_topic' #sending to this topic
TABLE = 'tumbling_table_1'
KAFKA = ['kafka://localhost:9092',"kafka://localhost:9093","kafka://localhost:9094"]
CLEANUP_INTERVAL = 10.0
WINDOW = 3
WINDOW_EXPIRES = 10
PARTITIONS = 1
app = faust.App('windowed-agg', broker=KAFKA, version=1, topic_partitions=1)

app.conf.table_cleanup_interval = CLEANUP_INTERVAL
source = app.topic(TOPIC, value_type = RawModel) #, value_type=list
sink = app.topic(SINK, value_type=AggModel_mean)


def window_processor(key, events):
    def mean(value,count):
        return sum(value) / count
    print(key)
    print(events)
    # events = {k: v for d in events for k, v in d.items()}
    timestamps = [event.Timestamp for event in events]
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


tumbling_table = (
    app.Table(
        TABLE,
        default=list,
        partitions=PARTITIONS,
        on_window_close=window_processor,
    )
    .tumbling(WINDOW, expires=timedelta(seconds=WINDOW_EXPIRES))
    .relative_to_field(RawModel.Timestamp)
)


@app.agent(source)
async def print_windowed_events(stream):
    async for event in stream:
        value_list = tumbling_table['events'].value()
        value_list.append(event)
        tumbling_table['events'] = value_list


# @app.timer(0.1)
# async def produce():
#     await source.send(value=RawModel(value=random.random(), date=int(time())))


if __name__ == '__main__':
    app.main()