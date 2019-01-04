# coding:utf-8

import re

from fetcher import IFetcher
from utils import WebRequest


class Fetcher(IFetcher):
    name = '快代理'
    source = 'www.kuaidaili.com'

    def fetch(self):
        url_list = [
            'https://www.kuaidaili.com/free/inha/%d/',
            'https://www.kuaidaili.com/free/intr/%d/'
        ]
        ret = []
        for url in url_list:
            for page in range(1, 5):
                page_url = url % page
                html = WebRequest.get(page_url, retry_time=1).text
                for i in re.findall(r'<td data-title="IP">(\S+)</td>\s+<td data-title="PORT">(\d+)</td>', html):
                    ret.append(':'.join(i))
        ret = list(set(ret))
        return ret


if __name__ == '__main__':
    print([_ for _ in Fetcher().fetch()])
