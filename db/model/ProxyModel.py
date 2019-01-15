# coding:utf-8
import _ssl
import asyncio
import re
import ssl
import time
from _sha1 import sha1
from datetime import datetime
from enum import IntEnum
from uuid import uuid4

from sqlalchemy import Column, String, SmallInteger, Enum, Integer, DateTime

from utils import Config
from utils.errors import ProxyEmptyRecvError, ProxyRecvError, ProxyTimeoutError, ProxySendError, ProxyConnError
from utils.functions import parse_headers
from verify.negotiators import NGTRS


def uid():
    return str(uuid4())


class Anonymity(IntEnum):
    Transparent = 0  # 透明代理
    Anonymous = 1  # 普通匿名
    Confuse = 2  # 混淆
    Elite = 3  # 高度匿名

    def __str__(self):
        return self.name


class ProxyModel(Config.Base):
    __tablename__ = 'proxy'
    unique_id = Column(String(40), primary_key=True, default=uid)
    ip = Column(String(15), nullable=False)
    port = Column(Integer, nullable=False)
    anonymity = Column(SmallInteger, default=1)
    protocol = Column(Enum('http', 'https', 'socks4', 'socks5', 'VPN'), default='http')
    speed = Column(Integer, default=0)
    ip_feedback = Column(String(255))
    extra_headers = Column(String(1024))
    usable = Column(SmallInteger, default=1)
    auth = Column(SmallInteger, default=0)
    success = Column(Integer, default=1)
    failed = Column(Integer, default=0)
    verified_at = Column(DateTime, default=datetime.now)  # Last time that passed verify
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    exception = None

    @property
    def uid(self):
        _sha1 = sha1()
        _sha1.update(self.url.encode())
        return _sha1.hexdigest()

    @classmethod
    def instance(cls, proxy: str):
        if not proxy:
            return None
        ret = re.findall(r'^(\w+)://(?:(\S*):(\S+)@)?(\S+?):(\d+)$', proxy)
        if not ret:
            return None
        return cls(*ret[0])

    def __init__(self, protocol, username='', password='', ip='', port=0):
        self.protocol = protocol
        self.ip = ip
        self.port = int(port)
        self.auth = False
        self.username = username
        self.password = password
        if username.strip() or password.strip():
            self.auth = True
        self.unique_id = self.uid

        self._ssl_context = ssl._create_unverified_context()
        self._closed = True
        self._reader = {'conn': None, 'ssl': None}
        self._writer = {'conn': None, 'ssl': None}
        self._timeout = 4

    def init(self):
        self._ssl_context = ssl._create_unverified_context()
        self._closed = True
        self._reader = {'conn': None, 'ssl': None}
        self._writer = {'conn': None, 'ssl': None}
        self._timeout = 4

    @property
    def url(self):
        return '%s://%s:%s' % (self.protocol, self.ip, self.port)

    def __str__(self):
        return self.url

    def __repr__(self):
        return '<usable=%s, url=%s, anonymity=%s, speed=%d>' % (
            self.usable, self.url, self.anonymity, self.speed
        )

    @property
    def writer(self):
        return self._writer.get('ssl') or self._writer.get('conn')

    @property
    def reader(self):
        return self._reader.get('ssl') or self._reader.get('conn')

    @property
    def ngtr(self):
        return NGTRS[self.protocol.upper()](self)

    async def connect(self, use_ssl=False):
        err = None
        msg = '%s' % 'SSL: ' if use_ssl else ''
        stime = time.time()
        self.log('%sInitial connection' % msg)
        try:
            if use_ssl:
                _type = 'ssl'
                sock = self._writer['conn'].get_extra_info('socket')
                params = {'ssl': self._ssl_context, 'sock': sock,
                          'server_hostname': self.ip}
            else:
                _type = 'conn'
                params = {'host': self.ip, 'port': self.port}
            self._reader[_type], self._writer[_type] = await asyncio.wait_for(asyncio.open_connection(**params), timeout=self._timeout)
        except asyncio.TimeoutError:
            msg += 'Connection: timeout'
            err = ProxyTimeoutError(msg)
            raise err
        except (ConnectionRefusedError, OSError, _ssl.SSLError):
            msg += 'Connection: failed'
            err = ProxyConnError(msg)
            raise err
        else:
            msg += 'Connection: success'
            self._closed = False
        finally:
            self.log(msg, stime, err=err)

    def close(self):
        if self._closed:
            return
        self._closed = True
        if self.writer:
            self.writer.close()
        self._reader = {'conn': None, 'ssl': None}
        self._writer = {'conn': None, 'ssl': None}
        self.log('Connection: closed')

    async def send(self, req):
        msg, err = '', None
        _req = req.encode() if not isinstance(req, bytes) else req
        try:
            self.writer.write(_req)
            await self.writer.drain()
        except ConnectionResetError:
            msg = 'Sending: ConnectionReset'
            err = ProxySendError(msg)
            raise err
        finally:
            self.log('Request: %s%s' % (req, msg), err=err)

    async def recv(self, length=0, head_only=False):
        resp, msg, err = b'', '', None
        stime = time.time()
        try:
            resp = await asyncio.wait_for(self._recv(length, head_only), timeout=self._timeout)
        except asyncio.TimeoutError:
            msg = 'Received: timeout'
            err = ProxyTimeoutError(msg)
            raise err
        except (ConnectionResetError, OSError) as e:
            msg = 'Received: failed'  # (connection is reset by the peer)
            err = ProxyRecvError(msg)
            raise err
        else:
            msg = 'Received: %s bytes' % len(resp)
            if not resp:
                err = ProxyEmptyRecvError(msg)
                raise err
        finally:
            if resp:
                msg += ': %s' % resp[:12]
            self.log(msg, stime, err=err)
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
        Config.logger.debug('%s: %s' % (self.url, msg))


if __name__ == '__main__':
    print(uid())
