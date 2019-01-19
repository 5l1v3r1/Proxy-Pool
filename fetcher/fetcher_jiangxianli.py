# coding:utf-8
import re

import gevent

from fetcher import BaseFetcher
from utils.functions import IPPortPatternGlobal


class Fetcher(BaseFetcher):
    name = 'jiangxianli'

    def __init__(self, tasks, result, pool=None):
        super(Fetcher, self).__init__(tasks, result, pool)
        self.urls = ['http://ip.jiangxianli.com/?page=%d' % i for i in range(1, 5)]

    @BaseFetcher.sleep(0.5)
    def handle(self, resp):
        return IPPortPatternGlobal.findall(resp.text)


if __name__ == '__main__':
    Fetcher.test()
