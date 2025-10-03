from gc import callbacks
from opcua import Client
from concurrent.futures import ThreadPoolExecutor,wait,as_completed
import yaml
from itertools import chain
from confluent_kafka import Producer,KafkaException
import logging
import json
import sys
import time
import os



def find_object_node_by_browsing(node, target_name, current_path=""):
    """
    Recursively search for a node in a tree-like structure based on its display name.

    This function traverses a tree-like structure rooted at 'node' and searches for a node with
    a display name that matches 'target_name'. It returns the first matching node and its path
    from the root node.

    Args:
        node: The root node of the tree-like structure to search.
        target_name (str): The display name of the node to search for.
        current_path (str, optional): The path from the root to the current node (used for recursion).
            Defaults to an empty string.

    Returns:
        tuple: A tuple containing:
            - The first matching node with the given 'target_name'.
            - The path from the root node to the matching node as a string.

        If no matching node is found, both elements of the tuple are None."""
    if node.get_display_name().Text == target_name:
        return node, current_path
    # Continue browsing child nodes
    for child_node in node.get_children():
        child_path = f"{current_path}/{child_node.get_display_name().Text}"
        result, node_path = find_object_node_by_browsing(child_node, target_name, child_path)
        if result:
            return result, node_path

    return None, None        

def find_children_attr(client,node_id):
    """
    Retrieve the children of a node and organize them in a dictionary.

    This function takes a 'client' object and a 'node_id' as input. It retrieves the children
    of the object node specified by 'node_id' using the 'client' object. The children
    are organized in a dictionary where the key is the display name of the 'node_id',
    and the values are a list of child nodes'.

    Args:
        client: An object representing the opc ua client used to interact with the system.
        node_id: The unique identifier of the object node whose children  you want to find.

    Returns:
        dict: A dictionary where the key is display name of 'node_id', and the values are lists
              of child nodes."""
    parent_child = {}
    try :
        # Get the object node by its path
        object_node = client.get_node(node_id)
        display_name_parent = object_node.get_display_name().Text
        children_attr = object_node.get_children()
        parent_child[display_name_parent]=children_attr
        return parent_child
    except  Exception as e:
        print(f"Error while finding children: {e}")
        return  e
    
def read_child_values(client ,child_id):
    """
    Retrieve and return the value of a child node identified by its 'child_id' using the 'client' object.

    Args:
        client (Client): An object representing an opc ua client for communication with a server.
        child_id (str): The unique identifier of the child node to retrieve.

    Returns:
        dict: A dictionary containing the child node's display name as the key and its value as the value.

    Raises:
        Exception: If an error occurs while attempting to retrieve the child node's value, an exception is raised.

    Note:
        - It checks the display name is "Imageblob" and decodes the value to convert it in a Unicode string
    """
    child_value_dict= {}
    try :
        node = client.get_node(child_id)
        display_name = node.get_display_name().Text
        #print("display name:",display_name)
        if display_name == "ImageBlob":
            value = node.get_value().decode('latin-1')   #blah
        else:
            value = node.get_value()
        child_value_dict[display_name]=value
        return child_value_dict
    except Exception as e:
        print(f"Error reading variable '{node.get_display_name().Text}':'{node}': {e}")
        return e
  
def send_records (producer,batch_values):
    """
    Send a batch of records to Kafka using the provided producer.

    Args:
        producer (Producer): An instance of a Kafka producer for sending records.
        batch_values (list): A list of dictionaries where each dictionary represents a batch of records.
                             Each dictionary should have a topic name as the key and a record value as the value.

    Returns:
        None

    Raises:
        Exception: If an error occurs during the sending process, an exception is logged as a warning, and the transaction is aborted.

    Note:
        - This function sends a batch of records to Kafka using the specified producer.
        - It begins a transaction, iterates through each batch of records, serializes them as JSON,
          and produces them to the corresponding Kafka topics.
        - After successfully producing all records, it commits the transaction.
    """
    logging.basicConfig(level=logging.WARNING)
    
    try:
        logging.info("Starting Transaction")
        # Begin a transaction
        producer.begin_transaction()
        for  batch_value in batch_values:
            for topic , value in batch_value.items():
                json_serealize = json.dumps(value)
                if producer is not None :
                    try:
                        producer.produce(topic ,value =json_serealize.encode('utf-8'),key = "key")
                    except KafkaException as ke:
                        print(f'Error occurred while producing message: {ke}')
                        return False                    
        logging.info ("Commiting Transaction")
        producer.commit_transaction()
        print(f"Sent a transaction to Kafka with {len(batch_value)} messages")
        #producer.flush() #ensure that any outstanding messages are delivered and delivery reports are received
        return True
    except KafkaException as ke:
        logging.warning(f"Kafka Error: {ke}")
        producer.abort_transaction()
        return False    
    except Exception as e:
        logging.warning(f"Failed to send message: {e}")
        producer.abort_transaction()
        return False

def connect_to_opcua_server(server_endpoint):
    """
    Connect to an OPC UA server at the specified server endpoint.

    Args:
        server_endpoint (str): The endpoint URL of the OPC UA server to connect to.

    Returns:
        Client: An OPC UA client object if the connection is successful, or None if there's an error.

    Note:
        - This function attempts to establish a connection to an OPC UA server using the provided server endpoint.
        - If an exception occurs during the connection process, it prints an error message and returns None.
    """
    try:
        client = Client(server_endpoint)
        client.connect()
        logging.info("Connected to the OPC UA server.")
        print("Connected to the OPC UA server.")
        return client
    except Exception as e:
        logging.warning(f"Error connecting to the OPC UA server: {str(e)}")
        print(f"Error connecting to the OPC UA server: {str(e)}")
        return None 
def produce_to_kafka(producer_config):
    try:
        producer = Producer(producer_config)
        return producer
    except Exception as e:
        print(f"Kafka Error: {e}")
        return None    



def find_parents_id(target_nodes,root):
    """
    Find node ids of the specified target nodes within a hierarchical tree structure.

    Args:
        target_nodes (list): A list of target node objects to find parent nodes for.
        root: The root node of the hierarchical tree structure.

    Returns:
        list: A list of node ids corresponding to the target nodes. If a parent is not found for a target node, it will be None in the list.

    Note:
        - This function searches for the parent nodes ids of the given target nodes within a hierarchical tree structure.
        - It iterates through the target nodes and invokes the 'find_object_node_by_browsing' function to locate each target node's id.
    """
    parents_node =[]
    for target_node in target_nodes:
        try:
            found_node, node_path = find_object_node_by_browsing(root, target_node)
            parents_node.append(found_node)
        except Exception as e :
            logging.warning(f"Error finding node {target_node}")
            parents_node.append(None)           
    return parents_node

def get_children_from_parents(parents_node,client):
    """
    Retrieve children nodes for a list of parent nodes using an OPC UA client.

    Args:
        parents_node (list): A list of parent node objects for which children nodes are to be retrieved.
        client: An OPC UA client for communication with the server.

    Returns:
        list: A list of children node IDs corresponding to the parent nodes. Inside the list there are dictionaries.

    Notes:
        - This function retrieves children nodes for a list of parent nodes using the provided OPC UA client.
        - It iterates through the 'parents_node' list, skipping None values.
        - For each non-None parent node, it invokes the 'find_children_attr' function to find and append children node IDs.
        - The resulting list contains the children node IDs for the provided parent nodes.
    """
    children_nodes = []
    for parent_node in parents_node:
        if parent_node is not None:
        # Traverse the nodes starting from the target node
            children_id = find_children_attr(client,parent_node)
            children_nodes.append(children_id)
            
    return children_nodes        

def get_children_values (children_nodes,client):
    """
    Retrieve values for children nodes using an OPC UA client.

    Args:
        children_nodes (list): A list of dictionaries, each containing child node IDs grouped by their parent node.
        client: An OPC UA client for communication with the server.

    Returns:
        list: A list of dictionaries representing the values of child nodes grouped by their parent nodes.

    Notes:
        - This function retrieves values for child nodes using the provided OPC UA client.
        - It processes each group of child nodes, where each group is represented as a dictionary.
        - For each group, it concurrently invokes the 'read_child_values' function for each child node using a ThreadPoolExecutor.
        - The 'read_child_values' function is called for each child node, and their values are collected and grouped by parent node.
        - The result is a list of dictionaries, where each dictionary represents the values of child nodes grouped by their parent nodes.
    """
    batch_values = []    
    for children_node in children_nodes:
        children_values = {}
        parent_child_values = {}
        children_node_list = list(chain.from_iterable(children_node.values()))
        #print("children node list:",len(children_node_list))
        children_node_key = list(children_node.keys())
        parent_node = children_node_key[0]
        #print("parent_node",parents_node)
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(read_child_values, client,node_id) for node_id in children_node_list]  
            # Wait for all futures to complete using as_completed
            wait(futures)
            for future in as_completed(futures):
                #print("printing future:",future.result())
                children_values.update(future.result())   
                #print("children_values:",children_values)                     
            parent_child_values[parent_node]=children_values
            #print("parent_child_values:",parent_child_values)
        batch_values.append(parent_child_values)
    print(batch_values)
    return batch_values        
                         
def read_config(path):
    """
    Read configuration settings from a YAML file named 'config.yml'.

    Returns:
        dict: A dictionary containing the configuration settings.

    Note:
        - If the file is successfully parsed, the settings are returned as a dictionary.
        - If any YAML parsing error occurs, the exception is printed, and the function returns None.
    """
    with open(path, "r") as ymlfile:
        try:
            cfg = yaml.full_load(ymlfile)
            return cfg
        except yaml.YAMLError as exc:
            print(exc)

if __name__ == "__main__":
    config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yml")
    cfg = read_config(config_file_path)
    opcua_server_url = cfg["opcua"]["endpoint"] 
    target_nodes = ["TimeseriesData","ImageData"]
   
    #Configuration settings for the Kafka producer.
    producer_config = {
    'bootstrap.servers': cfg["kafka"]["bootstrap"],
    'acks': cfg["kafka"]["acks"],
    'enable.idempotence':cfg["kafka"]["idempotence"],
    'compression.type':cfg["kafka"]["compressiontye"],
    'batch.size': cfg["kafka"]["batchsize"], 
    'linger.ms':cfg["kafka"]["lingerms"], 
    'client.id' : cfg["kafka"]["client"],
    'retries': cfg["kafka"]["retries"], 
    'delivery.timeout.ms':  cfg["kafka"]["deliverytimeout"],
    'request.timeout.ms': cfg["kafka"]["requesttimeout"],
    'transactional.id':  cfg["kafka"]["transactionalid"],
    'transaction.timeout.ms' : cfg["kafka"]["transactiontimeout"] }

   
    try: 
        opcua_client = connect_to_opcua_server(opcua_server_url)
        producer = produce_to_kafka(producer_config)
        if opcua_client is not None:
            root = opcua_client.get_root_node()
            #find the ids of the parents nodes sensors 
            parents_node=find_parents_id(target_nodes,root)
            children_nodes=get_children_from_parents(parents_node,opcua_client) #list with 2 dicctionaries inside [{'TimeseriesData': [Node(NumericNodeId(ns=2;i=2))},{'ImageData': [Node(NumericNodeId(ns=2;i=15))}]       
            # Initialize transactions
            producer.init_transactions()
            x= True
            while x == True:
                batch_values=get_children_values(children_nodes,opcua_client)
                x=send_records(producer=producer,batch_values =batch_values)
                time.sleep(5)
            
    finally :
        try:
            if batch_values :
                send_records(producer =producer,batch_values =batch_values)
                producer.flush()
                print("finish!")    
            # Disconnect from the OPC UA server
            if opcua_client is not None:
                opcua_client.disconnect() 
                print("finish!")
        except:
            if opcua_client is not None:
                opcua_client.disconnect() 
                print("finish!")    
        

       