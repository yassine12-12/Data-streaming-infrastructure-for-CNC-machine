from email.mime import image
from platform import node
from OPCUA_Server import OpcuaServer
from json_merger import merge_json_files
from image_read import ImageReader
from concurrent.futures import ThreadPoolExecutor, wait
import yaml
import time
import os

config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yml")
with open(config_file_path, "r") as ymlfile:
    try:
        cfg = yaml.full_load(ymlfile)
        print(cfg)
    except yaml.YAMLError as exc:
        print(exc)
# Get the values from the configuration file
endpoint = cfg["opcua"]["endpoint"]
address_space_name = cfg["opcua"]["adressspacename"] 
path_1 = cfg["opcua"]["timeseries1"]   
path_2 =  cfg["opcua"]["timeseries2"] 
path_3 = cfg["opcua"]["timeseries3"]   
path_img_folder = cfg["opcua"]["img"]  
node_timeseries =cfg["opcua"]["nodes"]["name1"]
node_image =cfg["opcua"]["nodes"]["name2"]

file_names = [path_1,path_2,path_3]
# Merge JSON files specified in the 'file_names' list , the function return a list
merged_data=merge_json_files(file_names)
# List all files in the 'path_img_folder' directory
image_list = os.listdir(path_img_folder)


def timeseries_processing():
    """
    Process and add timeseries data to a server.
    """
    for index, data in enumerate(merged_data):
        if index < 3:
            server.add_timeseries_data(data)
            values_time_series = server.get_timeseries_value()
            print(values_time_series)
            time.sleep(1)


def image_processing():
    """
    Process and add image data to a server.
    """
    for index, filename in enumerate(os.listdir(path_img_folder)):
        print(os.listdir(path_img_folder))
        if index < 3:
            if filename.endswith(".tiff"):
                image_reader = ImageReader(
                    filename=filename, folder=path_img_folder)
                # Read the image data and its timestamp    
                blob_data, image_timestamp = image_reader.read_image()
                # Add image data to the server 
                server.add_image_data(
                    blob_data=blob_data, image_creation_time=image_timestamp)
                values_image = server.get_image_value()
                print(values_image)
                time.sleep(1)


def timeseries_image_processing():
    """
    Process timeseries and image data and interact with a server.
    """
    pos= 0    
    while pos < 300 :
        # Get timeseries data at the current position from 'merged_data'
        timeseries_data = merged_data[pos]
        # Add timeseries data to the server 
        server.add_timeseries_data(timeseries_data)
        # Retrieve timeseries values from the server
        values_time_series = server.get_timeseries_value()
        print(values_time_series)
        # Get the image data filename at the current position from 'image_list'
        img_data_filename=image_list[pos]
        img_reader = ImageReader(filename=img_data_filename,folder=path_img_folder)
        # Read the image data and its timestamp
        img_blob,img_time = img_reader.read_image()
        # Add image data to the server 
        server.add_image_data(blob_data=img_blob,image_creation_time=img_time)
        values_image = server.get_image_value()
        print(values_image)
        pos=pos+1
        time.sleep(5)




if __name__ == "__main__":

    server = OpcuaServer(endpoint, address_space_name)
    server.start()
    server.create_address_space_timeseries(node_timeseries)
    server.create_address_space_image(node_image)

# read the timeseries values first and then the images
    timeseries_image_processing()
# process the timeseres values and the images simultaneously
    """with ThreadPoolExecutor() as executor:
        timeseries_future = executor.submit(timeseries_processing)
        image_future = executor.submit(image_processing)
        wait([timeseries_future, image_future])"""

    server.stop()
