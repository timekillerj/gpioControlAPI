import json
import logging

config = {}

try:
    with open('config.json') as json_data_file:
        config = json.load(json_data_file)
except OSError as e:
    logging.error("Error reading config.json: {}".format(e))


def get_pin(pin):
    logging.error("GETPIN LOOKING FOR PIN: {}".format(pin))
    for module in config:
        logging.error("GETPIN MODULE: {}".format(module))
        if module == 'main':
            continue
        for mode in ['output_pins', 'input_pins']:
            logging.error("GETPIN MODE: {}".format(mode))
            mylist = config[module][mode]
            logging.error("VAR TYPE: {}".format(type(mylist)))
            logging.error("GETPIN MODULE,MODE DATA: {}".format(mylist))
            logging.error("GETPIN LOOKING FOR {} in {}".format(pin, mylist))
            logging.error("GETPIN PIN TYPE: {}".format(type(pin)))
            for value in mylist:
                logging.error("GETPIN LIST VALUE TYPE: {}".format(type(value)))
                if pin in mylist:
                    logging.error("GETPIN FOUND PIN: {}, {}".format(module, mode))
                    return (module, mode)
        return (None, None)
