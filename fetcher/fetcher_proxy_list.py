# coding:utf-8
import base64
import re

import gevent

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = 'proxy-list'
    use_proxy = True

    def __init__(self, tasks, result, pool=None):
        super(Fetcher, self).__init__(tasks, result, pool)
        self.urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]

    def handle(self, resp):
        return re.findall(r"Proxy\('(.*?)'\)", resp.text)

    def add_result(self, result):
        for proxy in result:
            self._tasks.add(base64.b64decode(proxy).decode())


if __name__ == '__main__':
    Fetcher.test()
