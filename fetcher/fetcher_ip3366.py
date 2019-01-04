# coding:utf-8

import re

from fetcher import IFetcher
from utils import WebRequest


class Fetcher(IFetcher):
    name = 'ip3366'
    source = 'www.ip3366.net'

    def fetch(self):
        url = 'http://www.ip3366.net/free/?stype=%d&page=%d'
        request = WebRequest()
        ret = []
        for x in range(1, 5):
            for y in range(1, 6):
                r = request.get(url % (x, y))
                proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
                for proxy in proxies:
                    ret.append(":".join(proxy))
        ret = list(set(ret))
        return ret


if __name__ == '__main__':
    print([_ for _ in Fetcher().fetch()])
