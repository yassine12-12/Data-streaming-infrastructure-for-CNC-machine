from opcua import ua, Server


class OpcuaServer:
    def __init__(self, endpoint, address_space_name):
        self.server = Server()
        self.server.set_endpoint(endpoint)
        self.address_space =self.server.register_namespace(address_space_name)
        self.root_node =self.server.get_objects_node()
        self.timeseries_object = None
        self.image_object = None

    def create_address_space_timeseries(self,nodename):
        """
        Create a time series node and define variables for sensor measurements under the specified node.

        Args:
            nodename (str): The name of the node under which the time series node and variables will be created.

        Returns:
            None

        Note:
            - This method creates a new node for time series data under the specified "nodename" in the address space.
            - Several variables for different sensor measurements are defined under the time series node.
            - Each variable is initialized with an appropriate default value and data type.
        """
        # Create a new node for time series data under the specified "nodename"
        self.timeseries_object = self.root_node.add_object(self.address_space,nodename)
        # Define variables for various sensor measurements within the time series node
        self.timeseries_object_timestamp_variable = self.timeseries_object.add_variable(self.address_space, "Timestamp", ua.Variant(0, ua.VariantType.DateTime))
        self.timeseries_object_humidity_variable = self.timeseries_object.add_variable(self.address_space, "Humidity", ua.Variant(0.0, ua.VariantType.Float))
        self.timeseries_object_pressure_variable = self.timeseries_object.add_variable(self.address_space, "Pressure", ua.Variant(0.0, ua.VariantType.Float))
        self.timeseries_object_accelX_variable=self.timeseries_object.add_variable(self.address_space, "AccelX", ua.Variant(0, ua.VariantType.Int32))
        self.timeseries_object_accelY_variable =self.timeseries_object.add_variable(self.address_space, "AccelY", ua.Variant(0, ua.VariantType.Int32))
        self.timeseries_object_accelZ_variable =self.timeseries_object.add_variable(self.address_space, "AccelZ", ua.Variant(0, ua.VariantType.Int32))
        self.timeseries_object_gyroX_variable = self.timeseries_object.add_variable(self.address_space, "GyroX", ua.Variant(0, ua.VariantType.Int32))
        self.timeseries_object_gyroY_variable = self.timeseries_object.add_variable(self.address_space, "GyroY", ua.Variant(0, ua.VariantType.Int32))
        self.timeseries_object_gyroZ_variable = self.timeseries_object.add_variable(self.address_space, "GyroZ", ua.Variant(0, ua.VariantType.Int32))
        self.timeseries_object_T_variable = self.timeseries_object.add_variable(self.address_space, "T", ua.Variant(0.0, ua.VariantType.Float))
        self.timeseries_object_noise_variable = self.timeseries_object.add_variable(self.address_space, "Noise", ua.Variant(0.0, ua.VariantType.Float))
        self.timeseries_object_light_variable = self.timeseries_object.add_variable(self.address_space, "Light", ua.Variant(0.0, ua.VariantType.Float))

    def create_address_space_image(self,nodename):
        """
        Create a node for image-related data and define variables for image information.

        Args:
            nodename (str): The name of the node under which the image-related data node and variables will be created.

        Returns:
            None

        Note:
            - This method creates a new node for image-related data under the specified `nodename` in the address space.
            - Several variables for image-related information are defined under the image node.
            - Each variable is initialized with an appropriate default value and data type.
        """
        # Create a new node for image-related data under the specified `nodename`
        self.image_object = self.root_node.add_object(self.address_space,nodename) #"ImageData"
        # Define variables for image-related information within the image node
        self.image_object_timestamp = self.image_object.add_variable(self.address_space,"ImageTimestamp",ua.Variant(0, ua.VariantType.DateTime))
        self.image_object_blobdata= self.image_object.add_variable(self.address_space, "ImageBlob", ua.Variant([], ua.VariantType.ByteString))
        self.image_object_sensor =self.image_object.add_variable(self.address_space, "ImageSensor", ua.Variant([], ua.VariantType.ByteString))

    def add_timeseries_data(self,data):
        """
        Set timeseries data values for various sensor measurements.

        Args:
            data (dict): A dictionary containing timeseries data for various sensor measurements.

        Returns:
            None

        Note:
            - The data dictionary should contain corresponding keys and values for each measurement.
            - Each data value is set for its respective timeseries variable within the timeseries object.
        """
        self.timeseries_object_timestamp_variable.set_value(data["timestamp"])
        self.timeseries_object_humidity_variable.set_value(data["Humidity"])
        self.timeseries_object_pressure_variable.set_value(data["Pressure"])
        self.timeseries_object_accelX_variable.set_value(data["AccelX"])
        self.timeseries_object_accelY_variable.set_value(data["AccelY"])
        self.timeseries_object_accelZ_variable.set_value(data["AccelZ"])
        self.timeseries_object_gyroX_variable.set_value(data["GyroX"])
        self.timeseries_object_gyroY_variable.set_value(data["GyroY"])
        self.timeseries_object_gyroZ_variable.set_value(data["GyroZ"])
        self.timeseries_object_T_variable.set_value(data["T"])
        self.timeseries_object_noise_variable.set_value(data["Noise"])
        self.timeseries_object_light_variable.set_value(data["Light"])

    def add_image_data(self,blob_data,image_creation_time):
        """
        Set image-related data values.

        Args:
            blob_data (bytes): Binary image data.
            image_creation_time (datetime): Timestamp indicating when the image was created.

        Returns:
            None

        Note:
            - The 'blob_data' parameter should contain binary image data.
        """
        self.image_object_sensor.set_value("Basler")
        self.image_object_timestamp.set_value(image_creation_time)
        self.image_object_blobdata.set_value(blob_data)    
        
    def get_timeseries_value(self):
        """
        Retrieve timeseries data values for various sensor measurements.

        """
        timestamp = self.timeseries_object_timestamp_variable.get_value()
        humidity =self.timeseries_object_humidity_variable.get_value()
        pressure =self.timeseries_object_pressure_variable.get_value()
        accelX=self.timeseries_object_accelX_variable.get_value()
        accelY=self.timeseries_object_accelY_variable.get_value()
        accelZ=self.timeseries_object_accelZ_variable.get_value()
        gyroX=self.timeseries_object_gyroX_variable.get_value()
        gyroY=self.timeseries_object_gyroY_variable.get_value()
        gyroZ=self.timeseries_object_gyroZ_variable.get_value()
        t=self.timeseries_object_T_variable.get_value()
        noise=self.timeseries_object_noise_variable.get_value()
        light =self.timeseries_object_light_variable.get_value()
        return [timestamp, humidity ,pressure,accelX,accelY,accelZ,gyroX,gyroY,gyroZ,t,noise,light] 

    def get_image_value(self):
        """
        Retrieve image-related data values.

        """
        image_sensor = self.image_object_sensor.get_value()
        image_timestamp = self.image_object_timestamp.get_value()
        blob_data = self.image_object_blobdata.get_value()
        return [image_sensor,image_timestamp,"blah"]

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()

    """cual es la diferencia entro object y object type es mejor crear
    un object type anadirle al object type las variables (atributos) y ese type anadirselo a un object o
    trabajar directamente en un object!!!!! """
