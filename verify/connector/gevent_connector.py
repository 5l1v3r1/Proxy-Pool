# coding:utf-8

from gevent import ssl, socket

from verify.connector.base_connector import BaseConnector
from utils import LogHandler
from utils.errors import RecvTimeout, ConnectTimeout, ProxySendError
from utils.response import HTTPSocketResponse, HTTPConnectionClosed
from verify.negotiators import NGTRS

logger = LogHandler('GeventConnector')


class GeventConnector(BaseConnector):

    def __init__(self, protocol, ip, port, timeout=5):
        super(GeventConnector, self).__init__(protocol, ip, port, timeout)
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
        except ConnectionResetError:
            raise ProxySendError
        except Exception as e:
            logger.error('Error when send data: %s' % type(e))
            raise
        finally:
            logger.debug('Request: %s%s' % (req, msg))

    def recv(self, length=0, status_code=False):
        resp, msg, err = b'', 'Response', None
        try:
            resp = self._recv(length, status_code)
        except (socket.timeout, HTTPConnectionClosed):
            raise RecvTimeout
        except Exception as e:
            logger.debug('Error when recv data: %s' % type(e))
            raise
        logger.debug(msg)
        return resp

    def _recv(self, length=0, status_code=False):
        if length:
            resp = self.socket.recv(length)
        else:
            if status_code:
                tmp = self.socket.recv(4096)
                parts = tmp.split()
                if len(parts) > 1:
                    resp = int(parts[1].decode())
                    logger.debug('Status code: %d' % resp)
                else:
                    resp = 0
            else:
                parser = HTTPSocketResponse(self.socket)
                resp = self.decompress_content(parser, parser.read())
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

