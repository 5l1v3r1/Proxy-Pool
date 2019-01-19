import struct
from abc import ABC, abstractmethod
from socket import inet_aton

from utils import LogHandler
from utils.errors import BadStatusError, BadResponseError

__all__ = ['Socks5Ngtr', 'Socks4Ngtr', 'Connect80Ngtr', 'Connect25Ngtr',
           'HttpsNgtr', 'HttpNgtr', 'NGTRS']

SMTP_READY = 2201

logger = LogHandler('Negotiator')


def _CONNECT_request(host, port, **kwargs):
    kwargs.setdefault('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.321.132 Safari/537.36')
    kw = {
        'host': host,
        'port': port,
        'headers': '\r\n'.join(('%s: %s' % (k, v) for k, v in kwargs.items()))
    }
    req = 'CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}\r\n{headers}\r\nConnection: keep-alive\r\n\r\n'.format(**kw).encode()
    return req


class BaseNegotiator(ABC):
    """Base Negotiator."""

    name = None
    check_anon_lvl = False
    use_full_path = False

    def __init__(self, proxy):
        self._proxy = proxy

    @abstractmethod
    def negotiate(self, judge):
        """Negotiate with proxy."""


class Socks5Ngtr(BaseNegotiator):
    """SOCKS5 Negotiator."""

    name = 'SOCKS5'

    def negotiate(self, judge):
        self._proxy.send(struct.pack('3B', 5, 1, 0))
        resp = self._proxy.recv(2)
        try:
            if resp[0] == 0x05 and resp[1] == 0xff:
                raise BadResponseError('Failed (auth is required)')
            elif resp[0] != 0x05 or resp[1] != 0x00:
                raise BadResponseError('Failed (invalid data)')

            bip = inet_aton(judge.ip)
            port = judge.port

            self._proxy.send(struct.pack('>8BH', 5, 1, 0, 1, *bip, port))
            resp = self._proxy.recv(10)

            if resp[0] != 0x05 or resp[1] != 0x00:
                raise BadResponseError('Failed (invalid data)')
            else:
                logger.debug('Request is granted')
        except IndexError:
            raise BadResponseError('Socks5 protocol not supported')


class Socks4Ngtr(BaseNegotiator):
    """SOCKS4 Negotiator."""

    name = 'SOCKS4'

    def negotiate(self, judge):
        bip = inet_aton(judge.ip)
        port = judge.port

        self._proxy.send(struct.pack('>2BH5B', 4, 1, port, *bip, 0))
        resp = self._proxy.recv(8)

        if resp[0] != 0x00 or resp[1] != 0x5A:
            raise BadResponseError('Failed (invalid data)')
        # resp = b'\x00Z\x00\x00\x00\x00\x00\x00' // ord('Z') == 90 == 0x5A
        else:
            logger.debug('Request is granted')


class Connect80Ngtr(BaseNegotiator):
    """CONNECT Negotiator."""

    name = 'CONNECT:80'

    def negotiate(self, judge):
        self._proxy.send(_CONNECT_request(judge.host, 80))
        code = self._proxy.recv(status_code=True)
        if code != 200:
            raise BadStatusError('Connect: failed. HTTP status: %s' % code)


class Connect25Ngtr(BaseNegotiator):
    """SMTP Negotiator (connect to 25 port)."""

    name = 'CONNECT:25'

    def negotiate(self, judge):
        self._proxy.send(_CONNECT_request(judge.host, 25))
        code = self._proxy.recv(status_code=True)
        if code != 200:
            raise BadStatusError('Connect: failed. HTTP status: %s' % code)

        resp = self._proxy.recv(length=3)
        code = resp[0:3]
        if code != SMTP_READY:
            raise BadStatusError('Failed (invalid data): %s' % code)


class HttpsNgtr(BaseNegotiator):
    """HTTPS Negotiator (CONNECT + SSL)."""

    name = 'HTTPS'

    def negotiate(self, judge):
        self._proxy.send(_CONNECT_request(judge.host, 443))
        code = self._proxy.recv(status_code=True)
        if code != 200:
            raise BadStatusError('Connect: failed. HTTP status: %s' % code)
        self._proxy.connect(use_ssl=True)


class HttpNgtr(BaseNegotiator):
    """HTTP Negotiator."""

    name = 'HTTP'
    use_full_path = True

    def negotiate(self, judge):
        pass


NGTRS = {'HTTP': HttpNgtr, 'HTTPS': HttpsNgtr,
         'SOCKS4': Socks4Ngtr, 'SOCKS5': Socks5Ngtr,
         'CONNECT:80': Connect80Ngtr, 'CONNECT:25': Connect25Ngtr}
