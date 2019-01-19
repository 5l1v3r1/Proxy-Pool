# coding:utf-8
import re

import gevent

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = 'us-proxy'
    use_proxy = True

    def __init__(self, tasks, result, pool=None):
        super(Fetcher, self).__init__(tasks, result, pool)
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

    def handle(self, resp):
        return re.findall(r'<td>(\d+\.\d+\.\d+\.\d+).+?<td>(\d+)</td>', resp.text, re.S)


if __name__ == '__main__':
    Fetcher.test()
