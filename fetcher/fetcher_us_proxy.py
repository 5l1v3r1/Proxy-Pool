# coding:utf-8
import re

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = 'us-proxy'
    use_proxy = True

    def __init__(self, loop=None):
        super(Fetcher, self).__init__(loop)
        self.urls = [
            'https://www.us-proxy.org/',
            'https://www.socks-proxy.net/',
            'https://www.sslproxies.org/',
            'https://free-proxy-list.net/',
            'https://free-proxy-list.net/uk-proxy.html',
            'https://free-proxy-list.net/web-proxy.html',
            'https://free-proxy-list.net/anonymous-proxy.html',
            'http://www.google-proxy.net/'
        ]

    async def handle(self, resp):
        return re.findall(r'<td>(\d+\.\d+\.\d+\.\d+).+?<td>(\d+)</td>',
                          await resp.text(), re.S)


if __name__ == '__main__':
    Fetcher.test()
