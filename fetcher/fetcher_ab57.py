# coding:utf-8

import gevent

from fetcher import BaseFetcher
from utils.functions import IPPortPatternGlobal


class Fetcher(BaseFetcher):
    name = 'ab57'

    def __init__(self, tasks, result, pool=None):
        super(Fetcher, self).__init__(tasks, result, pool)
        self.urls = [
            'http://ab57.ru/downloads/proxyold.txt',
            'http://ab57.ru/downloads/proxylist.txt'
        ]

    def handle(self, resp):
        return IPPortPatternGlobal.findall(resp.text)


if __name__ == '__main__':
    Fetcher.test()
