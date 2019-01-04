# coding:utf-8

import re

from fetcher import IFetcher
from utils import WebRequest


class Fetcher(IFetcher):
    name = 'jiangxianli'
    source = 'www.jiangxianli.com'

    def fetch(self):
        url = 'http://ip.jiangxianli.com/?page=%d'
        ret = []
        for page in range(1, 5):
            page_url = url % page
            html = WebRequest.get(page_url, retry_time=1).text
            for i in re.findall(r'(?:\d{1,3}\.){3}\d{1,3}:\d+', html):
                ret.append(i)
        ret = list(set(ret))
        return ret


if __name__ == '__main__':
    print([_ for _ in Fetcher().fetch()])
