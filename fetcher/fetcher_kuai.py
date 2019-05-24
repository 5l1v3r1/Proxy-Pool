# coding:utf-8
import re

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = '快代理'

    def __init__(self, loop=None):
        super(Fetcher, self).__init__(loop)
        self.urls = ['https://www.kuaidaili.com/free/inha/%d/' % i for i in
                     range(1, 6)] + \
                    ['https://www.kuaidaili.com/free/intr/%d/' % i for i in
                     range(1, 6)]

    @BaseFetcher.sleep(0.5)
    async def handle(self, resp):
        return re.findall(
            r'<td data-title="IP">(\S+)</td>\s+<td data-title="PORT">(\d+)</td>',
            await resp.text())


if __name__ == '__main__':
    Fetcher.test()
