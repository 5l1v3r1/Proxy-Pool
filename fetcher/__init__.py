# coding:utf-8
from abc import ABC, abstractmethod

import gevent
import requests
from gevent.lock import BoundedSemaphore
from requests import Response

from utils import LogHandler, Config


class BaseFetcher(ABC):
    name = None
    enabled = True
    urls = []
    logger = LogHandler('Provider')
    use_proxy = False

    @staticmethod
    def sleep(sec):
        def decorator(func):  # 装饰器核心，以被装饰的函数对象为参数，返回装饰后的函数对象
            if sec:
                def wrapper(self, *args, **kvargs):  # 装饰的过程，参数列表适应不同参数的函数
                    self.lock.acquire()
                    try:
                        func(self, *args, **kvargs)  # 调用函数
                        gevent.sleep(sec)
                    except Exception as e:
                        self.logger.debug(e)
                    self.lock.release()

                return wrapper
            else:
                return func
        return decorator

    def __init__(self, tasks, result, pool=None):
        self._tasks = tasks
        self._result = result
        self.timeout = 5
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.321.132 Safari/537.36',
            'Accept': '*/*',
            'Pragma': 'no-cache',
            'Cache-control': 'no-cache',
            'Referer': 'https://www.google.com/'
        }
        self.pool = pool
        self.lock = BoundedSemaphore()
        self.prepare()  # must run after init

    def request(self, url):
        resp = self._request(url)
        proxies = self.handle(resp)
        self.add_result(proxies)

    def _request(self, url):
        if self.use_proxy:
            return requests.get(url, headers=self.headers, proxies={'http': 'http://' + Config.proxy, 'https': 'https://' + Config.proxy}, timeout=self.timeout)
        else:
            return requests.get(url, headers=self.headers, timeout=self.timeout)

    def prepare(self):
        pass

    def add_task(self, func):
        self._tasks.append(func)

    def add_result(self, result):
        if isinstance(result, (list, set)):
            for i in result:
                if isinstance(i, tuple):
                    self._result.add(':'.join(i))
                else:
                    self._result.add(i)
        elif isinstance(result, str):
            self._result.add(result)
        elif isinstance(result, tuple):
            self._result.add(':'.join(result))
        else:
            raise TypeError

    @abstractmethod
    def handle(self, resp: Response):
        pass

    def process_urls(self):
        return self.urls

    def fill_task(self):
        urls = self.process_urls()
        for url in urls:
            task = gevent.spawn(self.request, url)
            self.add_task(task)
            if self.pool is not None:
                self.pool.add(task)

    def __str__(self):
        return '<Provider name=%s, enabled=%s>' % (self.name, self.enabled)

    @classmethod
    def test(cls):
        tasks = []
        result = set()
        cls(tasks, result).fill_task()
        gevent.joinall(tasks)
        print(result)


__all__ = ['BaseFetcher']
