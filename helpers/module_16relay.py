from helpers import gpiohelper


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
