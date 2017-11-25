import logging
from .base import BaseHandler, require_shared_secret
import tornado.web
from tornado import gen

from helpers import GPIOHelper


class GPIOControlsHandler(BaseHandler):
    @require_shared_secret
    @gen.coroutine
    def get(self):
        gpio_pins = {}
        try:
            # TODO use filters for INPUT/OUTPUT
            gpio_pins['input_pins'] = GPIOHelper.read_input_pins()
            gpio_pins['output_pins'] = GPIOHelper.read_output_pins()
        except Exception as e:
            logging.error("Error reading pin states: {}".format(e))
            raise tornado.web.HTTPError(500, 'Error reading pin states: {}'.format(e))
        self.api_response(gpio_pins)


class GPIOControlHandler(BaseHandler):
    @require_shared_secret
    @gen.coroutine
    def get(self):
        pass
