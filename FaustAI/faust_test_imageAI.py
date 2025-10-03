import faust
import json
import cv2
import numpy as np
from PIL import Image

from ultralytics import YOLO

KAFKA = ['kafka://localhost:9092',"kafka://localhost:9093","kafka://localhost:9094"]



# Load a pretrained YOLOv8n model
model = YOLO(r".\train9\weights\best.pt")  # Load a Trained  model
#model = YOLO(r"FaustAI\yolov8n.pt")   Load a preTrained  model

app = faust.App(
    id='my-app',
    broker=KAFKA,
    value_serializer='raw', 
    store='memory://'
)

# consumer Topic definition
topic = app.topic('faust_sink_image')
# sink topic
sink = app.topic("faust_sink_image_AI")

# output data structure
class IMAGE_DATA(faust.Record, serializer='json'):
    ImageBlob: list
    ImageSensor: str
    shape: tuple

@app.agent(topic)
async def my_agent(stream):
    async for event in stream:
        data = json.loads(event)
        print(len(data.get("ImageBlob")))
        # reading pictures in the .jpg Format
        buf_array = np.frombuffer(bytes(data.get("ImageBlob")), dtype=np.uint8).reshape(data.get("shape"))#.reshape(buf.shape)
        img_np = cv2.imdecode(np.frombuffer (buf_array,np.uint8), cv2.IMREAD_UNCHANGED)

        # Run inference on 'bus.jpg' with arguments
        result = model.predict(img_np, show=True) #save prediction in resuslts 
        for r in result:
            im_array = r.plot()  # plot a BGR numpy array of predictions
            im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
            print("coco",type(im))
            img_jpg = im.convert("RGB") # convert the image to RGB mode
        # decode Image to the .jpg Format
        img_cv2 = cv2.cvtColor(np.array(img_jpg), cv2.COLOR_RGB2BGR)
        ret, buf = cv2.imencode('.jpg', img_cv2, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        # send Data back to the Broker
        await sink.send(value = IMAGE_DATA(ImageBlob = buf.tolist(), ImageSensor = data.get("ImageSensor"), shape = buf.shape))

         


if __name__ == '__main__':
    app.main()
