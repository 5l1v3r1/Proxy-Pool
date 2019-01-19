# coding:utf-8
import re

import gevent

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = 'proxylistplus'
    use_proxy = True

    def __init__(self, tasks, result, pool=None):
        super(Fetcher, self).__init__(tasks, result, pool)
        self.urls = [
            'https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1',
            'https://list.proxylistplus.com/SSL-List-1',
            'https://list.proxylistplus.com/Socks-List-1'
        ]

    def handle(self, resp):
        return re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', resp.text)


if __name__ == '__main__':
    Fetcher.test()
