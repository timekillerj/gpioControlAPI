#!/usr/bin/env python
import logging

from ConfigParser import SafeConfigParser
import tornado
import tornado.options
import tornado.web

from handlers import gpiocontrol


config = SafeConfigParser()
config.read('config.ini')


class HealthHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('OK')


class Application(tornado.web.Application):
    def __init__(self):
        app_settings = {
            'debug': config.get('main', 'debug'),
        }

        app_handlers = [
            (r'^/health/?$', HealthHandler),
            (r'^/v1/gpiocontrol/?$', gpiocontrol.GPIOControlsHandler),
            (r'^/v1/gpiocontrol/(\d+)/?$', gpiocontrol.GPIOControlHandler),
        ]
        super(Application, self).__init__(app_handlers, **app_settings)


if __name__ == '__main__':
    tornado.options.parse_command_line()

    port = config.get('main', 'port')
    address = '0.0.0.0'
    logging.info('starting gpiocontrol on %s:%d', address, port)

    http_server = tornado.httpserver.HTTPServer(request_callback=Application(), xheaders=True)
    http_server.listen(port, address=address)

    io_loop = tornado.ioloop.IOLoop.current()

    io_loop.set_blocking_log_threshold(1)  # warning on 1 sec blocked ioloop

    tornado.ioloop.IOLoop.instance().start()
