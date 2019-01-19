# coding:utf-8
import re

import gevent

from fetcher import BaseFetcher
from utils.functions import IPPortPatternGlobal


class Fetcher(BaseFetcher):
    name = 'my-proxy'
    use_proxy = True

    def __init__(self, tasks, result, pool=None):
        super(Fetcher, self).__init__(tasks, result, pool)
        self.urls = [
            'https://www.my-proxy.com/free-elite-proxy.html',
            'https://www.my-proxy.com/free-anonymous-proxy.html',
            'https://www.my-proxy.com/free-socks-4-proxy.html',
            'https://www.my-proxy.com/free-socks-5-proxy.html'
        ]

    def handle(self, resp):
        return IPPortPatternGlobal.findall(resp.text)


if __name__ == '__main__':
    Fetcher.test()
