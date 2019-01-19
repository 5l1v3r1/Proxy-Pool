# coding:utf-8

import gevent

from fetcher import BaseFetcher
from utils.functions import IPPortPatternGlobal


class Fetcher(BaseFetcher):
    name = 'baizhongsou'
    use_proxy = True

    def __init__(self, tasks, result, pool=None):
        super(Fetcher, self).__init__(tasks, result, pool)
        self.urls = ['http://ip.baizhongsou.com/']

    def handle(self, resp):
        return IPPortPatternGlobal.findall(resp.text)


if __name__ == '__main__':
    Fetcher.test()
