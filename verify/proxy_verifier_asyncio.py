# coding:utf-8
import asyncio
import datetime
import zlib
from functools import partial
from json import JSONDecodeError

from db.model import ProxyModel
from utils import LogHandler
from utils.config import Config
from utils.errors import (
    BadStatusError, BadResponseError, ProxyEmptyRecvError, ProxyConnError,
    ProxyTimeoutError, ProxyRecvError, ProxySendError)
from utils.functions import get_headers, get_status_code, parse_headers
from utils.functions import get_self_ip
from verify.judge import Judge

logger = LogHandler('ProxyAsyncVerifier')


class ProxyAsyncVerifier:
    def __init__(self, loop=None, post=False, timeout=4):
        self._loop = loop or asyncio.get_event_loop()
        self._real_ext_ip = get_self_ip()
        self._on_check = asyncio.Queue(maxsize=200, loop=self._loop)

        self._method = 'POST' if post else 'GET'
        self._real_ext_ip = get_self_ip()
        self.http_judge = Judge('http://httpbin.skactor.tk:8080', loop=loop)
        self.http_judge.event.set()
        self.https_judge = Judge('https://httpbin.skactor.tk', loop=loop)
        self.https_judge.event.set()
        self._all_tasks = []
        self.finished = 0

    def _done(self):
        while self._all_tasks:
            task = self._all_tasks.pop()
            if not task.done():
                task.cancel()

    async def _push_to_check(self, proxy):
        def _task_done(proxy, f):
            proxy.close()
            self._on_check.task_done()
            if not self._on_check.empty():
                self._on_check.get_nowait()

        await self._on_check.put(None)
        task = asyncio.ensure_future(self.check(proxy))
        task.add_done_callback(partial(_task_done, proxy))
        self._all_tasks.append(task)

    async def verify_proxy(self, proxies):
        for proxy in proxies:
            proxy.init()
            await self._push_to_check(proxy)
        await self._on_check.join()
        self._done()

    async def check(self, proxy: ProxyModel):
        if proxy.protocol == 'https':
            judge = self.https_judge
        else:
            judge = self.http_judge
        await judge.event.wait()
        content = None
        try:
            await proxy.connect()
            await proxy.ngtr.negotiate(judge)
            headers, content, hdrs = await _send_test_request(self._method, proxy, judge)
            content = _decompress_content(headers, content)
            judge.parse_response(proxy, content, hdrs)
        except ProxyTimeoutError as e:
            proxy.exception = e
        except (ProxyConnError, ProxyRecvError, ProxySendError, ProxyEmptyRecvError, BadStatusError, BadResponseError) as e:
            proxy.exception = e
        except JSONDecodeError:
            # Config.logger.error('Json decode error when using %s' % proxy)
            Config.logger.debug(content)
        except Exception as e:
            proxy.exception = e
            Config.logger.error('Error with proxy: %s, exception type: %s' % (proxy, type(e)))
            Config.logger.exception(e)
        finally:
            judge.event.set()
        proxy.verified_at = datetime.datetime.now()
        self.finished += 1
        return proxy


def _request(method, host, path, fullpath=False, data=''):
    hdrs = get_headers()
    hdrs['Host'] = host
    hdrs['Connection'] = 'close'
    if method == 'POST':
        hdrs['Content-Length'] = len(data)
        hdrs['Content-Type'] = 'application/octet-stream'
    else:
        data = ''
    kw = {
        'method': method,
        'path': 'http://%s%s' % (host, path) if fullpath else path,  # HTTP
        'headers': '\r\n'.join(('%s: %s' % (k, v) for k, v in hdrs.items())),
        'data': data
    }
    return '{method} {path} HTTP/1.1\r\n{headers}\r\n\r\n{data}'.format(**kw).encode(), hdrs


async def _send_test_request(method, proxy: ProxyModel, judge):
    resp, content, err = None, None, None
    request, hdrs = _request(method=method, host=judge.host, path=judge.path, fullpath=proxy.ngtr.use_full_path)
    try:
        await proxy.send(request)
        resp = await proxy.recv()
        code = get_status_code(resp)
        if code != 200:
            err = BadStatusError
            raise err
        headers, content, *_ = resp.split(b'\r\n\r\n', maxsplit=1)
    except ValueError:
        err = BadResponseError
        raise err
    finally:
        proxy.log('Get: %s' % ('success' if content else 'failed'))
        proxy.exception = err
        Config.logger.debug('{h}:{p} [{n}]: ({j}), response: {resp}'
                            .format(h=proxy.ip, p=proxy.port, n=proxy.ngtr.name, j=judge.url, resp=resp))
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
