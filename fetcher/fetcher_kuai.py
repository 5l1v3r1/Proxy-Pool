# coding:utf-8
import re

import gevent
from gevent.lock import BoundedSemaphore

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = '快代理'

    def __init__(self, tasks, result, pool=None):
        super(Fetcher, self).__init__(tasks, result, pool)
        self.urls = ['https://www.kuaidaili.com/free/inha/%d/' % i for i in range(1, 6)] + \
                    ['https://www.kuaidaili.com/free/intr/%d/' % i for i in range(1, 6)]

        self.lock = BoundedSemaphore()

    @BaseFetcher.sleep(0.5)
    def handle(self, resp):
        return re.findall(r'<td data-title="IP">(\S+)</td>\s+<td data-title="PORT">(\d+)</td>', resp.text)


if __name__ == '__main__':
    Fetcher.test()
