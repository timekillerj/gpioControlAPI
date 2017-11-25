import calendar


def _utf8(s):
    """encode a unicode string as utf-8"""
    if isinstance(s, unicode):
        return s.encode("utf-8")
    assert isinstance(s, str), "_utf8 expected a str, not %r" % type(s)
    return s


def _utf8_params(params):
    """encode a dictionary of URL parameters (including iterables) as utf-8"""
    isinstance(params, dict)
    encoded_params = []
    for k, v in params.items():
        if v is None:
            continue
        if isinstance(v, (int, long, float)):
            v = str(v)
        if isinstance(v, (list, tuple)):
            v = [_utf8(x) for x in v]
        else:
            v = _utf8(v)
        encoded_params.append((k, v))
    return dict(encoded_params)


def _utc_ts(dt):
    """convert a datetime object into a UNIX epoch timestamp"""
    return calendar.timegm(dt.utctimetuple())


def _ts_to_ms_hour_bucket(ts):
    """
    Converts a timestamp in millisecond resolution
    to its corresponding hour bucket in millseconds.
    """
    return ts - ts % 3600000


def _ts_to_second_hour_bucket(ts):
    """
    Converts a timestamp in millisecond resolution
    to its corresponding hour bucket in seconds.
    """
    ts /= 1000
    return ts - ts % 3600
