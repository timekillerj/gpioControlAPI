import json
import logging

PIN_MODES = {
    'input_pins': 'input',
    'output_pins': 'output',
}

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
                return (module, PIN_MODES[mode])
    return (None, None)
