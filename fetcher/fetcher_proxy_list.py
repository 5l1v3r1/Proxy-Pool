# coding:utf-8

import base64
import re

from fetcher import IFetcher
from utils import WebRequest, Config


class Fetcher(IFetcher):
    name = 'proxy-list'
    source = 'proxy-list.org'

    def fetch(self):
        urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
        ret = []
        if not Config.proxy:
            return
        for url in urls:
            r = WebRequest.get(url, proxies={'https': 'https://' + Config.proxy})
            proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
            for proxy in proxies:
                ret.append(base64.b64decode(proxy).decode())
        ret = list(set(ret))
        return ret


if __name__ == '__main__':
    print([_ for _ in Fetcher().fetch()])
