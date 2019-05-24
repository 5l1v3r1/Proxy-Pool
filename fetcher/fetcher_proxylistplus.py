# coding:utf-8
import re

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = 'proxylistplus'
    use_proxy = True

    def __init__(self, loop=None):
        super(Fetcher, self).__init__(loop)
        self.urls = [
            'https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1',
            'https://list.proxylistplus.com/SSL-List-1',
            'https://list.proxylistplus.com/Socks-List-1'
        ]

    async def handle(self, resp):
        return re.findall(
            r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>',
            await resp.text())


if __name__ == '__main__':
    Fetcher.test()
