# coding:utf-8

from gevent import ssl, socket

from connector.base_connector import BaseConnector
from utils import LogHandler
from utils.errors import RecvTimeout, ConnectTimeout
from utils.functions import parse_headers
from utils.response import HTTPSocketResponse
from verify.negotiators import NGTRS

logger = LogHandler('GeventConnector')


class GeventConnector(BaseConnector):

    def __init__(self, protocol, ip, port, timeout=5):
        super(GeventConnector, self).__init__(protocol, ip, port, timeout)
        self.__size_recvd = 0
        self._socket = {'conn': None, 'ssl': None}
        self.negotiator = NGTRS[self.protocol.upper()](self)
        self.use_full_path = self.negotiator.use_full_path
        self.parser = None

    def negotiate(self, judge):
        self.negotiator.negotiate(judge)

    @property
    def socket(self):
        return self._socket.get('ssl') or self._socket.get('conn')

    @socket.setter
    def socket(self, value):
        if self._socket.get('conn'):
            self._socket['conn'] = value
        else:
            self._socket['ssl'] = value

    def connect(self, use_ssl=False):
        msg = '%s' % 'SSL: ' if use_ssl else ''
        logger.debug('%s Initial connection' % msg)
        try:
            if use_ssl:
                msg += 'Connection: Warp with SSL'
                self.socket = ssl.wrap_socket(self.socket)
            else:
                msg += 'Connection: Start connecting'
                self.socket = socket.create_connection((self.ip, self.port), timeout=self._timeout)
                self.socket.settimeout(self._timeout)
                self.parser = HTTPSocketResponse(self.socket)
        except socket.timeout:
            raise ConnectTimeout
        except Exception as e:
            raise
        else:
            msg += 'Connection: success'
            self._closed = False
        finally:
            logger.debug(msg)

    def close(self):
        if self._closed:
            return
        self._closed = True
        if self.socket:
            self.socket.close()
        self._socket = {'conn': None, 'ssl': None}

    def send(self, req):
        msg, err = '', None
        _req = req.encode() if not isinstance(req, bytes) else req
        try:
            self.socket.sendall(_req)
        except Exception as e:
            logger.error('Error when send data: %s' % type(e))
            raise
        finally:
            logger.debug('Request: %s%s' % (req, msg))

    def recv(self, length=0, head_only=False):
        resp, msg, err = b'', 'Response', None
        try:
            resp = self._recv(length, head_only)
        except socket.timeout:
            raise RecvTimeout
        except Exception as e:
            logger.debug('Error when recv data: %s' % type(e))
            raise
        if resp:
            msg += ': %s' % resp[:12]
        logger.debug(msg)
        return resp

    def _recv(self, length=0, head_only=False):
        resp = b''
        if length:
            resp = self.socket.recv(length)
        else:
            body_size, body_recv, chunked = 0, 0, None
            while True:
                line = self._recvline()
                if len(line) == 0:
                    break
                resp += line
                if body_size:
                    body_recv += len(line)
                    if body_recv >= body_size:
                        break
                elif chunked and line == b'0\r\n':
                    break
                elif not body_size and line == b'\r\n':
                    if head_only:
                        break
                    headers = parse_headers(resp)
                    body_size = int(headers.get('Content-Length', 0))
                    if not body_size:
                        chunked = headers.get('Transfer-Encoding') == 'chunked'
        return resp

    def _recvline(self):
        resp = b''
        while True:
            b = self.socket.recv(1)
            if len(b) == 0:
                break
            resp += b
            if b == b'\r\n':
                break
        return resp
