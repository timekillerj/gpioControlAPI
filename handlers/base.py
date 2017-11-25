import cgi
import json
import logging
import tornado.httpclient
import tornado.web
from ConfigParser import SafeConfigParser

# from lib import web_mixins
from concurrent.futures import ThreadPoolExecutor

config = SafeConfigParser()
config.read('config.ini')


def require_shared_secret(f):
    def decorated(self, *args, **kwargs):
        shared_secret = self.request.headers.get('X-Shared-Secret')
        if not shared_secret:
            logging.info('Request Missing shared_secret')
            raise tornado.web.HTTPError(401, 'MISSING_SHARED_SECRET')
        if shared_secret != config.get('main', 'shared_secret'):
            logging.error('Invalid Shared Secret')
            raise tornado.web.HTTPError(403, 'INVALID_SHARED_SECRET')
        return f(self, *args, **kwargs)
    return decorated


# class BaseHandler(tornado.web.RequestHandler, web_mixins.ApiMixin):
class BaseHandler(tornado.web.RequestHandler):
    '''Base request handler.

    Adds a some convenience methods for writing json and a standard
    error handler.
    '''

    thread_pool = ThreadPoolExecutor(max_workers=config.get('main', 'max_threads'))
    http = tornado.httpclient.AsyncHTTPClient()

    def write_error(self, status_code, **kwargs):
        '''Rewrites errors to a more standard format and writes a json response.'''
        if 'exc_info' not in kwargs:
            logging.error('NO_EXCEPTION_FOR_ERROR: {} {}'.format(status_code, kwargs))
            msg = 'INTERNAL_ERROR'
        else:
            _, error, _ = kwargs['exc_info']

            if isinstance(error, tornado.web.MissingArgumentError):
                msg = 'MISSING_ARG_{}'.format(error.arg_name.upper())
            elif isinstance(error, tornado.web.HTTPError):
                reason = '_'.join(self._reason.upper().split())
                msg = error.log_message or reason or 'INTERNAL_ERROR'
            else:
                msg = 'INTERNAL_ERROR'

        return self.api_response(msg, status_code)

    def api_response(self, data, code=200):
        '''Write a json response.

        If the response is an error, data is assumed to be a message and added
        to a 'message' key.
        '''
        self.set_status(code)
        self.set_header('Content-Type', 'application/json')

        if not 200 <= code < 300:
            data = {'message': data}

        if not isinstance(data, basestring):
            data = json.dumps(data)
        self.finish(data)

    @property
    def json_body(self):
        '''Parses and caches json bodies.'''
        if not hasattr(self, '_json_body'):
            content_type, _ = cgi.parse_header(self.request.headers.get('Content-Type', 'text/plain'))
            if content_type != 'application/json':
                raise tornado.web.HTTPError(415, 'INVALID_CONTENT_TYPE')

            try:
                self._json_body = json.loads(self.request.body)
            except ValueError:
                raise tornado.web.HTTPError(400, 'INVALID_JSON')

        return self._json_body


class MissingHandler(BaseHandler):
    '''Default handler to raise 404s.

    The default handler returns html. This inherits from BaseHandler which
    will write a json response instead.
    '''

    def prepare(self):
        '''Raise a 404 immediately.'''
        super(MissingHandler, self).prepare()
        raise tornado.web.HTTPError(404)
