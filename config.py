import json
import logging

config = {}

try:
    with open('config.json') as json_data_file:
        config = json.load(json_data_file)
except OSError as e:
    logging.error("Error reading config.json: {}".format(e))
