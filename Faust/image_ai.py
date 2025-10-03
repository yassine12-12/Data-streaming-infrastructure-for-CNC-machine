import cv2
import numpy as np
from PIL import Image 
Image.MAX_IMAGE_PIXELS = None
import PIL
import zlib
import sys
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
#sys.path.append("D:/Tucloud/Shared/Entwicklung von der Daten-Streaming-Infrastruktur im KI-Labor/05 Software/OPC UA/daten-streaming-infrastruktur/")
image= cv2.imread('images.jpeg') #Road-lanes.jpg'

# der Weg mit zlib nur ca. 30% erspraniss 1398159 -> 1010645
#image_bytes = resized_image.tobytes()
#image_compressed = zlib.compress(image_bytes, level=9)
#print(sys.getsizeof(resized_image))
#print(sys.getsizeof(image_compressed))
#image_decompressed = zlib.decompress(image_compressed)
#re_image = np.frombuffer(image_bytes, dtype=resized_image.dtype).reshape(resized_image.shape)
#print(np.array_equal(re_image, resized_image))


#cv2.imshow('Resized Image', resized_image)
#cv2.imshow('Region of Interest', region_of_interest_image)

# Als Jpeg zwischen speichern
"""
ret, buf = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
print(sys.getsizeof(buf))
print(type(buf.dtype))
img = cv2.imdecode(np.frombuffer(buf, np.uint8), cv2.IMREAD_COLOR) 
#cv2.imwrite('img1.jpg', resized_image, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
cv2.imshow('compressed Image', img)
"""
result = model.predict(image)
print(result[0].orig_img)

for r in result:
    im_array = r.plot()  # plot a BGR numpy array of predictions
    #print("bococo",type(im_array))
    im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
    print("coco",type(im))
    #im.show()
    img_jpg = im.convert("RGB") # convert the image to RGB mode
img_jpg.save("test.jpg")
img = cv2.cvtColor(np.array(img_jpg), cv2.COLOR_RGB2BGR)
cv2.imshow("Image3", img)

#img = Image.fromarray(buf) # this converts the numpy array to an image object
#img.save('img1.jpg') # this saves the image to a file
#cv2.imwrite('a.jpg', buf)

cv2.waitKey(12000)
cv2.destroyAllWindows()