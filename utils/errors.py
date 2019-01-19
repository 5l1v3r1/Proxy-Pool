"""Errors."""
from gevent import socket


class ProxyError(Exception):
    pass


class NoProxyError(Exception):
    pass


class ResolveError(Exception):
    pass


class ProxyConnError(ProxyError):
    errmsg = 'connection_failed'


class ProxyRecvError(ProxyError):
    errmsg = 'connection_is_reset'


class ProxySendError(ProxyError):
    errmsg = 'connection_is_reset'


class ProxyTimeoutError(ProxyError):
    errmsg = 'connection_timeout'


class ProxyEmptyRecvError(ProxyError):
    errmsg = 'empty_response'


class BadStatusError(Exception):  # BadStatusLine
    errmsg = 'bad_status'


class BadResponseError(Exception):
    errmsg = 'bad_response'


class BadStatusLine(Exception):
    errmsg = 'bad_status_line'


class ConnectTimeout(socket.timeout):
    pass


class RecvTimeout(socket.timeout):
    pass


class HTTPBadHeader(Exception):
    pass
