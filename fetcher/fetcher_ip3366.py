# coding:utf-8
import re

import gevent

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = 'ip3366'

    def __init__(self, tasks, result, pool=None):
        super(Fetcher, self).__init__(tasks, result, pool)
        self.urls = []
        for i in range(1, 5):
            for j in range(1, 6):
                self.urls.append('http://www.ip3366.net/free/?stype=%d&page=%d' % (i, j))

    @BaseFetcher.sleep(0.5)
    def handle(self, resp):
        return re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', resp.text)


if __name__ == '__main__':
    Fetcher.test()
