# coding:utf-8
import asyncio
import ssl

from utils import Config
from utils.errors import ProxyEmptyRecvError, ProxyRecvError, ProxySendError, \
    ProxyConnError, ProxyConnectTimeoutError, \
    ProxyRecvTimeoutError
from utils.functions import parse_headers


class Connector:
    def __init__(self, host, port, timeout=5):
        self.host = host
        self.port = port
        self._ssl_context = None
        self._closed = True
        self._reader = {'conn': None, 'ssl': None}
        self._writer = {'conn': None, 'ssl': None}
        self._timeout = timeout

    @property
    def writer(self):
        return self._writer.get('ssl') or self._writer.get('conn')

    @property
    def reader(self):
        return self._reader.get('ssl') or self._reader.get('conn')

    async def connect(self, use_ssl=False):
        try:
            if use_ssl:
                if not self._ssl_context:
                    self._ssl_context = ssl._create_unverified_context()
                _type = 'ssl'
                sock = self._writer['conn'].get_extra_info('socket')
                params = {'ssl': self._ssl_context, 'sock': sock,
                          'server_hostname': self.host}
            else:
                _type = 'conn'
                params = {'host': self.host, 'port': self.port}
            self._reader[_type], self._writer[_type] = await asyncio.wait_for(
                asyncio.open_connection(**params), timeout=self._timeout)
        except RuntimeError as e:
            raise ProxyConnError()
        except asyncio.TimeoutError:
            raise ProxyConnectTimeoutError('Connection: timeout')
        except (ConnectionRefusedError, OSError, ssl.SSLError):
            raise ProxyConnError('Connection: failed')
        else:
            self._closed = False

    def close(self):
        if self._closed:
            return
        self._closed = True
        sock = self._writer['conn'].get_extra_info('socket')
        if self.writer:
            self.writer.close()
        if sock:
            sock.close()
        self._reader = {'conn': None, 'ssl': None}
        self._writer = {'conn': None, 'ssl': None}
        self.log('Connection: closed')

    async def send(self, req):
        _req = req.encode() if not isinstance(req, bytes) else req
        try:
            self.writer.write(_req)
            await self.writer.drain()
        except ConnectionResetError:
            raise ProxySendError('Sending: ConnectionReset')

    async def recv(self, length=0, head_only=False):
        try:
            resp = await asyncio.wait_for(
                self._recv(length, head_only), timeout=self._timeout)
        except asyncio.TimeoutError:
            raise ProxyRecvTimeoutError('Received: timeout')
        except (ConnectionResetError, OSError) as e:
            raise ProxyRecvError('Received: failed')
        if not resp:
            raise ProxyEmptyRecvError('Empty Receive')
        return resp

    async def _recv(self, length=0, head_only=False):
        resp = b''
        if length:
            try:
                resp = await self.reader.readexactly(length)
            except asyncio.IncompleteReadError as e:
                resp = e.partial
        else:
            body_size, body_recv, chunked = 0, 0, None
            while not self.reader.at_eof():
                line = await self.reader.readline()
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

    def log(self, msg, *args, **kwargs):
        Config.logger.debug('%s:%d - %s' % (self.host, self.port, msg))
