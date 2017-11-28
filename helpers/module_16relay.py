from helpers import gpiohelper

PIN_STATES = {
    0: "on",
    1: "off",
}


class Module_16Relay(gpiohelper.GPIOHelper):
    """
    TODO: Document quirks of relay board
    """
    def __init__(self):
        super(Module_16Relay, self).__init__(module='module_16relay')

    def set_output_high(self, pin):
        self.set_pin_output(pin)

    def set_output_low(self, pin):
        self.set_pin_input(pin)

    def set_pin_input(self, pin):
        super(Module_16Relay, self).set_pin_input(pin)
        # Revert pin list assignment
        if pin in self.input_pins:
            self.input_pins.remove(pin)
        if pin not in self.output_pins:
            self.output_pins.append(pin)
