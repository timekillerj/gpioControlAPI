import logging
from .base import BaseHandler, require_shared_secret
import tornado.web
from tornado import gen

from helpers import gpiohelper
from helpers import module_16relay
from config import get_pin

gpio = gpiohelper.GPIOHelper()
module_16relay = module_16relay.Module_16Relay()


class GPIOControlsHandler(BaseHandler):
    @require_shared_secret
    @gen.coroutine
    def get(self):
        gpio_pins = {}
        module_16relay_pins = {}
        try:
            # TODO use filters for INPUT/OUTPUT
            if gpio:
                gpio_pins['input_pins'] = gpio.read_input_pins()
                gpio_pins['output_pins'] = gpio.read_output_pins()
            if module_16relay:
                module_16relay_pins['input_pins'] = module_16relay.read_input_pins()
                module_16relay_pins['output_pins'] = module_16relay.read_output_pins()
        except Exception as e:
            logging.error("Error reading pin states: {}".format(e))
            raise tornado.web.HTTPError(500, 'Error reading pin states: {}'.format(e))
        all_pins = {
            "gpio": gpio_pins,
            "module_16relay": module_16relay_pins
        }
        self.api_response(all_pins)


class GPIOControlHandler(BaseHandler):
    @require_shared_secret
    @gen.coroutine
    def get(self, pin):
        module, mode = get_pin(pin)
        logging.error('PIN: {}: {}, {}'.format(pin, module, mode))
        self.api_response(pin)
