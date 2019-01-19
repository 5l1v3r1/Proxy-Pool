# coding:utf-8
import re

import gevent

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = 'mrhinkydink'
    use_proxy = True

    def __init__(self, tasks, result, pool=None):
        super(Fetcher, self).__init__(tasks, result, pool)
        self.urls = ['http://www.mrhinkydink.com/proxies.htm'] + \
                    ['http://www.mrhinkydink.com/proxies%d.htm' % i for i in range(2, 10)]

    def handle(self, resp):
        return re.findall(r'<td>(\d+\.\d+\.\d+\.\d+).+?<td>(\d+)</td>', resp.text,re.S)


if __name__ == '__main__':
    Fetcher.test()
