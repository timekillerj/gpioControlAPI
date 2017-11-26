import RPi.GPIO as GPIO
import logging

from config import config


class GPIOHelper(object):
    def __init__(self, module='gpio'):
        self.output_pins = config.get(module, {}).get('output_pins')
        self.input_pins = config.get(module, {}).get('input_pins')
        logging.info("MODULE: {}".format(module))
        logging.info("INPUTS: {}".format(self.input_pins))
        logging.info("OUTPUTS: {}".format(self.output_pins))

        if not self.output_pins and not self.input_pins:
            return False

        if config.get(module, {}).get('mode') == "BCM":
            GPIO.setmode(GPIO.BCM)
        else:
            GPIO.setmode(GPIO.BOARD)

        # Set pin modes
        for pin in self.input_pins:
            logging.error("INPUT_PINS: {}".format(self.input_pins))
            self.set_pin_input(pin)

        for pin in self.output_pins:
            self.set_pin_output(pin)

    def set_pin_output(self, pin, state=GPIO.LOW):
        try:
            GPIO.setup(int(pin), GPIO.OUT, initial=state)
            if pin in self.input_pins:
                self.input_pins.remove(pin)
            if pin not in self.output_pins:
                self.output_pins.append(pin)
        except Exception as e:
            logging.error("Error setting {} as OUTPUT with state {}: {}".format(pin, state, e))

    def set_pin_input(self, pin):
        try:
            GPIO.setup(int(pin), GPIO.IN)
            if pin in self.output_pins:
                self.output_pins.remove(pin)
            if pin not in self.input_pins:
                self.input_pins.append(pin)
        except Exception as e:
            logging.error("Error setting {} as INPUT: {}".format(pin, e))

    def read_output_pins(self):
        output_pins = {}
        for pin in self.output_pins:
            pin_state = self.read_pin(pin)
            output_pins[pin] = pin_state
        return output_pins

    def read_input_pins(self):
        input_pins = {}
        for pin in self.input_pins:
            pin_state = self.read_pin(pin)
            input_pins[pin] = pin_state
        return input_pins

    def read_pin(self, pin):
        try:
            state = GPIO.input(int(pin))
        except Exception as e:
            logging.error("Error reading pin OUTPUT state: {}".format(e))
        return state

    def set_output_high(self, pin):
        try:
            GPIO.output(pin, GPIO.HIGH)
        except Exception as e:
            logging.error("Error setting output pin {} HIGH: {}".format(pin, e))

    def set_output_low(self, pin):
        try:
            GPIO.output(pin, GPIO.LOW)
        except Exception as e:
            logging.error("Error setting output pin {} LOW: {}".format(pin, e))
