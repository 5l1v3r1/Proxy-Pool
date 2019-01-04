# coding:utf-8

import re

from fetcher import IFetcher
from utils import WebRequest


class Fetcher(IFetcher):
    name = 'goubanjia'
    source = 'www.goubanjia.com'

    def fetch(self):
        url_list = [
            'http://www.goubanjia.com/'
        ]
        ret = []
        for url in url_list:
            html = WebRequest.get(url, retry_time=1).text
            html = re.sub(r"<p style='display:\s*none;'>\S*</p>", '', html)
            html = re.sub(r'</?(span|div).*?>', '', html)
            for i in re.findall(r'(\d+\.\d+\.\d+\.\d+):(\d+)', html):
                ret.append(':'.join(i))
        ret = list(set(ret))
        return ret


if __name__ == '__main__':
    print([_ for _ in Fetcher().fetch()])
