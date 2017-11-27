import logging
from .base import BaseHandler, require_shared_secret
import tornado.web
from tornado import gen
import json

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
        pin = int(pin)
        (module, mode) = get_pin(pin)
        if not module:
            raise tornado.web.HTTPError(404, 'PIN_NOT_ASSIGNED')
        elif module == 'gpio':
            state = gpio.read_pin(pin)
        elif module == 'module_16relay':
            state = module_16relay.read_pin(pin)
        response = {
            "pin": pin,
            "mode": mode,
            "state": state
        }
        self.api_response(response)

    @require_shared_secret
    @gen.coroutine
    def post(self, pin):
        """
        TODO: explain data
        data:
        set_output: low/high
        set_mode: output/input
        """
        data = json.loads(self.request.body)
        set_mode = data.get('set_mode', None)
        set_output = data.get('set_output', None)

        pin = int(pin)
        (module, mode) = get_pin(pin)
        if not module:
            raise tornado.web.HTTPError(404, 'PIN_NOT_ASSIGNED')
        elif module == 'gpio':
            gpio_module = gpio
        elif module == 'module_16relay':
            gpio_module = module_16relay

        if set_mode and set_mode != mode:
            if set_mode == "output":
                gpio_module.set_pin_output(pin)
                mode = set_mode
            elif set_mode == "input":
                gpio_module.set_pin_input(pin)
                mode = set_mode
            else:
                raise tornado.web.HTTPError(400, 'INVALID_MODE_VALUE')

        if set_output and mode == 'output':
            if set_output == 'high':
                gpio_module.set_output_high(pin)
            elif set_output == 'low':
                gpio_module.set_output_low(pin)
            else:
                raise tornado.web.HTTPError('400', 'INVALID_OUTPUT_VALUE')

            state = gpio_module.read_pin(pin)
            response = {
                "pin": pin,
                "mode": mode,
                "state": state
            }
            self.api_response(response)
