import json
import logging

config = {}

try:
    with open('config.json') as json_data_file:
        config = json.load(json_data_file)
except OSError as e:
    logging.error("Error reading config.json: {}".format(e))


def get_pin(pin):
    for module in config:
        if module == 'main':
            continue
        for mode in ['output_pins', 'input_pins']:
            if pin in config[module][mode]:
                return (module, mode)
