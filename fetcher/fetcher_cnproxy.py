# coding:utf-8

import re

from fetcher import IFetcher
from utils import WebRequest


class Fetcher(IFetcher):
    name = 'CN_PROXY'
    source = 'cn-proxy.com'

    def fetch(self):
        """
        无忧代理 http://www.data5u.com/
        几乎没有能用的
        """
        urls = [
            'https://cn-proxy.com'
        ]
        ret = []
        request = WebRequest()
        for url in urls:
            r = WebRequest.get(url, retry_time=1)
            proxies = re.findall(r'((?:\d{1,3}\.){3}\d{1,3})</td>\s*<td>(\d+)</td>', r.text)
            for proxy in proxies:
                ret.append(':'.join(proxy))
        ret = list(set(ret))
        return ret


if __name__ == '__main__':
    print([_ for _ in Fetcher().fetch()])
