# coding:utf-8

from fetcher import BaseFetcher
from utils.functions import IPPortPatternGlobal


class Fetcher(BaseFetcher):
    name = 'jiangxianli'

    def __init__(self, loop=None):
        super(Fetcher, self).__init__(loop)
        self.urls = ['http://ip.jiangxianli.com/']

    @BaseFetcher.sleep(0.5)
    async def handle(self, resp):
        return IPPortPatternGlobal.findall(await resp.text())


if __name__ == '__main__':
    Fetcher.test()
