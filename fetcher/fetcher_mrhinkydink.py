# coding:utf-8
import re

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = 'mrhinkydink'
    use_proxy = True

    def __init__(self, loop=None):
        super(Fetcher, self).__init__(loop)
        self.urls = ['http://www.mrhinkydink.com/proxies.htm'] + \
                    ['http://www.mrhinkydink.com/proxies%d.htm' % i for i in
                     range(2, 10)]

    async def handle(self, resp):
        return re.findall(r'<td>(\d+\.\d+\.\d+\.\d+).+?<td>(\d+)</td>',
                          await resp.text(), re.S)


if __name__ == '__main__':
    Fetcher.test()
