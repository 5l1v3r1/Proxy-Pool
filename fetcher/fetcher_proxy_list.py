# coding:utf-8
import base64
import re

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = 'proxy-list'
    use_proxy = True

    def __init__(self, loop=None):
        super(Fetcher, self).__init__(loop)
        self.urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n
                     in range(1, 10)]

    async def handle(self, resp):
        return re.findall(r"Proxy\('(.*?)'\)", await resp.text())

    def parse_proxy(self, result):
        tasks = set()
        for proxy in result:
            tasks.add(base64.b64decode(proxy).decode())
        return tasks


if __name__ == '__main__':
    Fetcher.test()
