# coding:utf-8

import re

from fetcher import IFetcher
from utils import WebRequest


class Fetcher(IFetcher):
    name = '无忧代理'
    source = 'www.data5u.com'

    def fetch(self):
        """
        无忧代理 http://www.data5u.com/
        几乎没有能用的
        """
        url_list = [
            'http://www.data5u.com/',
            'http://www.data5u.com/free/gngn/index.shtml',
            'http://www.data5u.com/free/gnpt/index.shtml',
            'http://www.data5u.com/free/gwgn/index.shtml',
            'http://www.data5u.com/free/gwpt/index.shtml'
        ]
        ret = []
        for url in url_list:
            html = WebRequest.get(url, retry_time=1).text
            for i in re.findall(r'(\d+\.\d+\.\d+\.\d+)[\S\s]+?(\d+)</li></span>', html):
                ret.append(':'.join(i))
        ret = list(set(ret))
        return ret


if __name__ == '__main__':
    print([_ for _ in Fetcher().fetch()])
