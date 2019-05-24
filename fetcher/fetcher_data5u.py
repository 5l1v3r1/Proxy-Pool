# coding:utf-8
import re

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = 'data5u'

    def __init__(self, loop=None):
        super(Fetcher, self).__init__(loop)
        self.urls = [
            'http://www.data5u.com/',
            'http://www.data5u.com/free/gngn/index.shtml',
            'http://www.data5u.com/free/gnpt/index.shtml',
            'http://www.data5u.com/free/gwgn/index.shtml',
            'http://www.data5u.com/free/gwpt/index.shtml'
        ]

    @BaseFetcher.sleep(2)
    async def handle(self, resp):
        return re.findall(r'(\d+\.\d+\.\d+\.\d+)[\S\s]+?(\d+)</li></span>',
                          await resp.text())


if __name__ == '__main__':
    Fetcher.test()
