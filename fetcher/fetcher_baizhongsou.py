# coding:utf-8

from fetcher import BaseFetcher
from utils.functions import IPPortPatternGlobal


class Fetcher(BaseFetcher):
    name = 'baizhongsou'
    use_proxy = True

    def __init__(self, loop=None):
        super(Fetcher, self).__init__(loop)
        self.urls = ['http://ip.baizhongsou.com/']

    async def handle(self, resp):
        return IPPortPatternGlobal.findall(await resp.text())


if __name__ == '__main__':
    Fetcher.test()
