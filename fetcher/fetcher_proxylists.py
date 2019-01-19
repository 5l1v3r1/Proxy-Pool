# coding:utf-8

import gevent

from fetcher import BaseFetcher
from utils.functions import IPPortPatternGlobal


class Fetcher(BaseFetcher):
    name = 'proxylists'

    def __init__(self, tasks, result, pool=None):
        super(Fetcher, self).__init__(tasks, result, pool)
        self.urls = [
            'http://www.proxylists.net/http.txt',
            'http://www.proxylists.net/http_highanon.txt',
            'http://www.proxylists.net/socks5.txt',
            'http://www.proxylists.net/socks4.txt'
        ]

    def handle(self, resp):
        return IPPortPatternGlobal.findall(resp.text)


if __name__ == '__main__':
    Fetcher.test()
