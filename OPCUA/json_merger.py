import json


def merge_json_files(file_names):
    merged_data = []

    for file_name in file_names:
        with open(file_name, "r") as file:
            data = json.load(file)
            merged_data.extend(data)
    return merged_data
