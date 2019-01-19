# coding:utf-8
import re

import gevent

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = 'data5u'

    def __init__(self, tasks, result, pool=None):
        super(Fetcher, self).__init__(tasks, result, pool)
        self.urls = [
            'http://www.data5u.com/',
            'http://www.data5u.com/free/gngn/index.shtml',
            'http://www.data5u.com/free/gnpt/index.shtml',
            'http://www.data5u.com/free/gwgn/index.shtml',
            'http://www.data5u.com/free/gwpt/index.shtml'
        ]

    @BaseFetcher.sleep(2)
    def handle(self, resp):
        return re.findall(r'(\d+\.\d+\.\d+\.\d+)[\S\s]+?(\d+)</li></span>', resp.text)


if __name__ == '__main__':
    Fetcher.test()
