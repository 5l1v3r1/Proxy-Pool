# coding:utf-8
import re

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = 'CN_PROXY'
    enable = False
    use_proxy = True

    def __init__(self, loop=None):
        super(Fetcher, self).__init__(loop)
        self.urls = [
            'https://cn-proxy.com/feed',
            'https://cn-proxy.com/archives/218'
        ]

    async def handle(self, resp):
        return re.findall(r'((?:\d{1,3}\.){3}\d{1,3})</td>\s*<td>(\d+)</td>',
                          await resp.text())


if __name__ == '__main__':
    Fetcher.test()
