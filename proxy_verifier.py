# coding:utf-8
import asyncio
import datetime
import zlib
from json import JSONDecodeError

from connector import Connector
from model import ProxyModel
from negotiators import NGTRS
from utils import Logger
from utils.errors import (
    BadStatusError, BadResponseError, ProxyError)
from utils.functions import get_status_code, parse_headers
from judge import Judge

logger = Logger('ProxyAsyncVerifier')


class ProxyAsyncVerifier:
    def __init__(self, loop=None, post=False, timeout=4):
        self._loop = loop or asyncio.get_event_loop()
        self._method = 'POST' if post else 'GET'
        self.finished = 0
        self.sem = asyncio.Semaphore(300)
        self.https_judge = Judge('https://httpbin.skactor.tk/anything')
        self.http_judge = Judge('http://httpbin.skactor.tk:8080/anything')

    async def _push_to_check(self, proxy):
        async with self.sem:
            await self.check(proxy)
        return proxy

    def verify(self, proxies):
        tasks = []
        for proxy in proxies:
            tasks.append(asyncio.ensure_future(self._push_to_check(proxy)))
        return tasks

    async def check(self, proxy: ProxyModel):
        logger.debug('Start Verify Proxy: %s' % proxy)
        proxy.usable = False
        judge = self.https_judge if proxy.protocol == 'https' else self.http_judge
        content = None
        conn = Connector(proxy.ip, proxy.port)
        negotiator = NGTRS[proxy.protocol.upper()](conn)
        try:
            await conn.connect()
            await negotiator.negotiate(judge)
            headers, content, hdrs = await _send_test_request(
                self._method, conn, negotiator, judge)
            content = _decompress_content(headers, content)
            judge.parse_response(proxy, content, hdrs)
        except ProxyError:
            pass
        except JSONDecodeError:
            # Config.logger.error('Json decode error when using %s' % proxy)
            logger.debug(content)
        except Exception as e:
            logger.error('Error: %s, type: %s' % (proxy, type(e)),
                         exc_info=True)
        finally:
            conn.close()
        proxy.verified_at = datetime.datetime.now()
        self.finished += 1
        logger.debug('Finished Proxy: %s' % (proxy))
        return proxy


async def _send_test_request(method, conn, ngtr, judge):
    resp, content, err = None, None, None
    request, hdrs = judge.gen_request(
        method=method, fullpath=ngtr.use_full_path)
    try:
        await conn.send(request)
        resp = await conn.recv()
        code = get_status_code(resp)
        if code != 200:
            raise BadStatusError()
        headers, content, *_ = resp.split(b'\r\n\r\n', maxsplit=1)
    except ValueError:
        raise BadResponseError()
    finally:
        logger.debug('Get: %s' % ('success' if content else 'failed'))
        logger.debug('{h}:{p} [{n}]: ({j}), response: {resp}'
                     .format(h=conn.host, p=conn.port, n=ngtr.name,
                             j=judge.url, resp=resp))
    return headers, content, hdrs


def _decompress_content(headers, content):
    headers = parse_headers(headers)
    is_compressed = headers.get('Content-Encoding') in ('gzip', 'deflate')
    is_chunked = headers.get('Transfer-Encoding') == 'chunked'
    if is_compressed:
        # gzip: zlib.MAX_WBITS|16;
        # deflate: -zlib.MAX_WBITS;
        # auto: zlib.MAX_WBITS|32;
        if is_chunked:
            # b'278\r\n\x1f\x8b...\x00\r\n0\r\n\r\n' => b'\x1f\x8b...\x00
            content = b''.join(content.split(b'\r\n')[1::2])
        try:
            content = zlib.decompress(content, zlib.MAX_WBITS | 32)
        except zlib.error:
            content = b''
    return content.decode('utf-8', 'ignore')
