# coding:utf-8

from fetcher import BaseFetcher
from utils.functions import IPPortPatternGlobal


class Fetcher(BaseFetcher):
    name = 'proxylists'

    def __init__(self, loop=None):
        super(Fetcher, self).__init__(loop)
        self.urls = [
            'http://www.proxylists.net/http.txt',
            'http://www.proxylists.net/http_highanon.txt',
            'http://www.proxylists.net/socks5.txt',
            'http://www.proxylists.net/socks4.txt'
        ]

    async def handle(self, resp):
        return IPPortPatternGlobal.findall(await resp.text())


if __name__ == '__main__':
    Fetcher.test()
