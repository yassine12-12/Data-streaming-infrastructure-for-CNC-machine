
import os
from PIL import Image
import io
class ImageReader:
    def __init__(self, filename,folder):
        # Initialize the folder path
        self.filename = filename
        self.folder = folder
    def read_image(self):
        img_path = os.path.join(self.folder, self.filename)
        with open(img_path, "rb") as f:
            img = Image.open(io.BytesIO(f.read()))
            # Create a file-like object in memory
            blob = io.BytesIO()
            # Save the image data as bytes
            img.save(blob, format='JPEG')
            #Return bytes containing the entire contents of the buffer.
            blob_data = blob.getvalue()
            creation_time = os.path.getctime(img_path)
        return blob_data, creation_time
