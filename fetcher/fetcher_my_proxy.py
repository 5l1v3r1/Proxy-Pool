# coding:utf-8

from fetcher import BaseFetcher
from utils.functions import IPPortPatternGlobal


class Fetcher(BaseFetcher):
    name = 'my-proxy'
    use_proxy = True

    def __init__(self, loop=None):
        super(Fetcher, self).__init__(loop)
        self.urls = [
            'https://www.my-proxy.com/free-elite-proxy.html',
            'https://www.my-proxy.com/free-anonymous-proxy.html',
            'https://www.my-proxy.com/free-socks-4-proxy.html',
            'https://www.my-proxy.com/free-socks-5-proxy.html'
        ]

    async def handle(self, resp):
        return IPPortPatternGlobal.findall(await resp.text())


if __name__ == '__main__':
    Fetcher.test()
