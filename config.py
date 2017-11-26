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
        logging.error("GETPIN MODULE: {}".format(module))
        if module == 'main':
            continue
        for mode in ['output_pins', 'input_pins']:
            logging.error("GETPIN MODE: {}".format(mode))
            logging.error("GETPIN MODULE,MODE DATA: {}".format(config[module][mode]))
            if pin in config[module][mode]:
                logging.error("GETPIN FOUND PIN: {}, {}".format(module, mode))
                return (module, mode)
