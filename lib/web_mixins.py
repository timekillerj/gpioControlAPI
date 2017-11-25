import datetime
import functools
import json
import logging
import urllib

import tornado.gen
import tornado.httpclient

try:
    from formatters import _utf8_params
except ImportError:
    from .formatters import _utf8_params

try:
    import settings
except ImportError:
    from .rig import settings


class ApiMixin(object):
    def __init__(self):
        super(ApiMixin, self).__init__()
        # settings
        self.allow_304 = False
        self.http_sync = tornado.httpclient.HTTPClient()
        self.http = tornado.httpclient.AsyncHTTPClient()

    def _create_api_request(self, method, path, params=None, body=None, headers=None, api_host=None, api_url=None,
                            set_content_type=True):
        headers = headers or {}

        if set_content_type:
            headers['Content-Type'] = 'application/json'

        if api_host is None:
            api_host = settings.get('api_host')
        if api_host:
            headers['Host'] = api_host

        api_url = api_url or settings.get('api_url')
        url = api_url + path

        if params and (method == 'GET' or method == 'DELETE' or body):
            url += '?' + urllib.urlencode(_utf8_params(params), doseq=True)
        elif params and not body:
            body = params
        if body and isinstance(body, dict):
            body = urllib.urlencode(_utf8_params(body), doseq=True)

        return tornado.httpclient.HTTPRequest(
            url=url, method=method, follow_redirects=False, headers=headers,
            body=body)

    def api_request_sync(self, method, path, **kwargs):
        req = self._create_api_request(method, path, **kwargs)
        try:
            resp = self.http_sync.fetch(req)
        except tornado.httpclient.HTTPError as e:
            return e.code, self._parse_api_response(e.response)
        else:
            return resp.code, self._parse_api_response(resp)

    @tornado.gen.coroutine
    def api_request(self, method, path, **kwargs):
        cb_args, cb_kwargs = yield tornado.gen.Task(
            self._api_request_helper, method, path, **kwargs)
        code = cb_kwargs.get('code')
        data = cb_kwargs.get('data')
        raise tornado.gen.Return((code, data))

    def _api_request_helper(self, method, path, callback=None, passthrough=False, **kwargs):
        req = self._create_api_request(method, path, **kwargs)
        internal_callback = functools.partial(
            self._finish_api_request, passthrough=passthrough,
            callback=callback)
        self.http.fetch(req, internal_callback)

    def _parse_api_response(self, response, passthrough=False):
        logging.debug('finished %d %s %s %0.2fms',
                      response.code, response.request.method,
                      response.request.url, response.request_time * 1000)
        if passthrough and 200 <= response.code < 300:
            return response.body
        elif hasattr(self, 'allow_304') and self.allow_304 and response.code == 304:  # cache
            return None  # No body for 304 responses
        response_data = json.loads(response.body)
        if not 200 <= response.code < 300:
            logging.error('got error %d from api endpoint %r: %r' % (
                response.code, response.request.url, response_data))
            return response_data.get('message', 'INTERNAL_ERROR')
        return response_data

    def _finish_api_request(self, response, callback, passthrough):
        try:
            response_data = self._parse_api_response(response, passthrough=passthrough)
        except Exception:
            logging.error('failed to decode API response for endpoint %r: %r - %r',
                          response.request.url, response.body, response.error)
            return callback(code=500, data='INTERNAL_ERROR')
        return callback(code=response.code, data=response_data)

    def api_response(self, data, code=200):
        self.set_status(code)
        self.set_header('Content-Type', 'application/json')
        if not 200 <= code < 300:
            data = {'message': data}
        if not isinstance(data, str):
            data = json.dumps(data)
        self.finish(data)


class HandlesDateRange(object):
    """
    Mixin for a tornado.web.RequestHandler class that will let it handle
    requests that specify a date range in a couple of ways:

     - ?days=N
     - ?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD

    The start and end dates will be parsed according to the date_format class
    attribute.
    """

    date_format = '%Y-%m-%d'

    def get_date_range_params(self):
        days = self.get_argument('days', None)
        if days:
            try:
                return {'days': int(days)}
            except ValueError:
                raise tornado.web.HTTPError(400, 'INVALID_DAYS')

        def parse_date(s):
            return datetime.datetime.strptime(s, self.date_format)

        try:
            start_date = parse_date(self.get_argument('start_date'))
        except ValueError:
            raise tornado.web.HTTPError(400, 'INVALID_START_DATE')
        try:
            end_date = parse_date(self.get_argument('end_date'))
        except ValueError:
            raise tornado.web.HTTPError(400, 'INVALID_END_DATE')
        return {
            'start_date': start_date.strftime(self.date_format),
            'end_date': end_date.strftime(self.date_format)
        }
