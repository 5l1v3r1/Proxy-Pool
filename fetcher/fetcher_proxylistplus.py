# coding:utf-8

import re

from fetcher import IFetcher
from utils import WebRequest


class Fetcher(IFetcher):
    name = 'proxy-list'
    source = 'proxy-list.org'

    def fetch(self):
        urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-%d' % n for n in range(1, 6)]
        ret = []
        for url in urls:
            r = WebRequest.get(url)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                ret.append(':'.join(proxy))
        ret = list(set(ret))
        return ret


if __name__ == '__main__':
    print([_ for _ in Fetcher().fetch()])
