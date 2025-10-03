import faust
import json
import cv2
import numpy as np
from PIL import Image
import zlib
# Definition der Daten Broker Ports
KAFKA = ['kafka://localhost:9092',"kafka://localhost:9093","kafka://localhost:9094"]

# Definition der Faust App
app = faust.App(
    id='my-app',
    broker=KAFKA,
    value_serializer='raw', 
    store='memory://'
)

# Consumer Topic
topic = app.topic('ImageData')
# Sink Topic
sink = app.topic("faust_sink_image")

# Datenformat zum senden der Daten
class IMAGE_DATA(faust.Record, serializer='json'):
    ImageBlob: list
    ImageSensor: str
    shape: tuple

# Anfang der Faust Anwendung
@app.agent(topic)
async def my_agent(stream):
    async for event in stream:

        # Laden der Daten aus dem JSON Format
        data = json.loads(event)
        print(len(data.get("ImageBlob")))
        # Dekodierung der gesendeten Daten
        byte_data = bytes(data.get("ImageBlob"),'latin-1')
        
        # speichern des Bildes im open_cv Format
        image = cv2.imdecode(np.frombuffer (byte_data,np.uint8), cv2.IMREAD_UNCHANGED)
        # Verkleinerung des Bildes durch wählen einer Region of Intrest
        height, width= image.shape[:2]
        print(height ,width)
        image_gray= cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #   Wahl des Bereiches, in diesem Fall um den Fräskopf 
        ROI= np.array([[(width/3,height/2),(width/3,0*height/2),(2*width/3,0*height/2),(2*width/3,height/2)]], dtype= np.int32)
        blank= np.zeros_like(image_gray)
        region_of_interest= cv2.fillPoly(blank, ROI,255)
        region_of_interest_image= cv2.bitwise_and(image_gray, region_of_interest)
        # Eckpunkte des zugeschnittenen Bildes
        x, y, w, h = cv2.boundingRect(region_of_interest)
        cropped_image = image[y:y+h, x:x+w]
        resized_image = cv2.resize(cropped_image, (h, w))

        # speichern  des Bildes im .JPG Format
        ret, buf = cv2.imencode('.jpg', resized_image, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        # senden der Daten zurück an den Broker
        await sink.send(value = IMAGE_DATA(ImageBlob = buf.tolist(), ImageSensor = data.get("ImageSensor"), shape = buf.shape)) # IMAGE_DATA(ImageBlob = resized_image.tolist(), ImageSensor = data.get("ImageSensor"))

if __name__ == '__main__':
    app.main()
