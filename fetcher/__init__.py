# coding:utf-8
import asyncio
from abc import ABC, abstractmethod

import aiohttp
from aiohttp import ClientTimeout, ClientConnectionError
from aiohttp_proxy import ProxyConnector

from utils import Logger, Config


class BaseFetcher(ABC):
    name = None
    enable = True
    urls = []
    logger = Logger('Provider')
    use_proxy = False

    @staticmethod
    def sleep(sec):
        def decorator(func):  # 装饰器核心，以被装饰的函数对象为参数，返回装饰后的函数对象
            if sec:
                async def wrapper(self, *args, **kwargs):  # 装饰的过程，参数列表适应不同参数的函数
                    async with self.lock:
                        try:
                            await func(self, *args, **kwargs)  # 调用函数
                            await asyncio.sleep(sec)
                        except Exception as e:
                            self.logger.debug(e)

                return wrapper
            else:
                return func

        return decorator

    def __init__(self, loop=None):
        self.timeout = 5
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.321.132 Safari/537.36',
            'Accept': '*/*',
            'Pragma': 'no-cache',
            'Cache-control': 'no-cache',
            'Referer': 'https://www.google.com/',
            'Connection': 'close'
        }
        self.loop = loop or asyncio.get_event_loop()
        self.lock = asyncio.Lock(loop=self.loop)

    async def fetch(self, url):
        try:
            resp = await self._request(url)
            proxies = await self.handle(resp)
            result = list(self.parse_proxy(proxies))
        except (asyncio.TimeoutError, ClientConnectionError):
            return []
        except Exception as e:
            self.logger.exception('Failed to fetch: ' + url)
            return []
        return result

    async def _request(self, url):
        connector = None
        if self.use_proxy:
            if not Config.proxy:
                raise Exception('Proxy must be if you use it!')
            connector = ProxyConnector.from_url(Config.proxy)
        async with aiohttp.ClientSession(
                connector=connector,
                timeout=ClientTimeout(total=10)) as session:
            async with session.get(url, headers=self.headers,
                                   verify_ssl=False) as resp:
                await resp.read()
        return resp

    def prepare(self):
        pass

    def parse_proxy(self, result):
        _result = set()
        if isinstance(result, (list, set)):
            for i in result:
                if isinstance(i, tuple):
                    _result.add(':'.join(i))
                else:
                    _result.add(i)
        elif isinstance(result, str):
            _result.add(result)
        elif isinstance(result, tuple):
            _result.add(':'.join(result))
        elif result is None:
            self.logger.warning(self.name + ' Return None')
        else:
            raise TypeError('Unknown proxy type: ' + str(type(result)))
        return _result

    @abstractmethod
    async def handle(self, resp):
        return []

    def process_urls(self):
        return self.urls

    def gen_tasks(self):
        self.prepare()  # must run after init
        urls = self.process_urls()
        tasks = []
        for url in urls:
            task = asyncio.ensure_future(self.fetch(url),loop=self.loop)
            tasks.append(task)
        return tasks

    def __str__(self):
        return '<Provider name=%s, enabled=%s>' % (self.name, self.enable)

    @classmethod
    def test(cls):
        loop = asyncio.get_event_loop()
        tasks = cls(loop).gen_tasks()
        loop.run_until_complete(asyncio.gather(*tasks))


__all__ = ['BaseFetcher']
