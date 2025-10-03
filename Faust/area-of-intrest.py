import cv2
import numpy as np
from PIL import Image 
Image.MAX_IMAGE_PIXELS = None
import PIL
import zlib
import sys
image= cv2.imread('images.jpeg') #Road-lanes.jpg'


height, width= image.shape[:2]
print(height ,width)
factor_width = 0.9
factor_height = 1.1
image_gray= cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
ROI= np.array([[(factor_width*width/3,factor_height*height/2),(factor_width*width/3,0*height/2),(2*width/3,0*height/2),(2*width/3,factor_height*height/2)]], dtype= np.int32)
blank= np.zeros_like(image_gray)
region_of_interest= cv2.fillPoly(blank, ROI,255)
region_of_interest_image= cv2.bitwise_and(image_gray, region_of_interest)
x, y, w, h = cv2.boundingRect(region_of_interest)
cropped_image = image[y:y+h, x:x+w]
#resized_image = cv2.resize(cropped_image, (region_of_interest_image.shape[1], region_of_interest_image.shape[0]))
resized_image = cv2.resize(cropped_image, (h, w))
#ratio = 400.0 / image.shape[0]
#dimension = (int(image.shape[1] * ratio), 400)

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
ret, buf = cv2.imencode('.jpg', resized_image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
print(sys.getsizeof(buf))
print(type(buf.dtype))
print(resized_image.dtype)
buf_bytes = buf.tobytes()
print(buf.tobytes()==buf.tostring())
buf_array = np.frombuffer(buf_bytes, dtype=resized_image.dtype).reshape(buf.shape)#.reshape(buf.shape)
img = cv2.imdecode(np.frombuffer(buf_array, np.uint8), cv2.IMREAD_COLOR) 
#cv2.imwrite('img1.jpg', resized_image, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
cv2.imshow('compressed Image', img)

#img = Image.fromarray(buf) # this converts the numpy array to an image object
#img.save('img1.jpg') # this saves the image to a file
#cv2.imwrite('a.jpg', buf)

cv2.waitKey(5000)
cv2.destroyAllWindows()