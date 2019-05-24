"""Errors."""


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
    errmsg = 'timeout'


class ProxyConnectTimeoutError(ProxyTimeoutError, ProxyConnError):
    errmsg = 'connect timeout'


class ProxyEmptyRecvError(ProxyRecvError):
    errmsg = 'empty_response'


class ProxyRecvTimeoutError(ProxyTimeoutError, ProxyRecvError):
    errmsg = 'receive timeout'


class BadStatusError(ProxyError):  # BadStatusLine
    errmsg = 'bad_status'


class BadResponseError(ProxyError):
    errmsg = 'bad_response'


class BadStatusLine(ProxyError):
    errmsg = 'bad_status_line'


class ErrorOnStream(ProxyError):
    errmsg = 'error_on_stream'
