# coding:utf-8
import re

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = 'ip3366'

    def __init__(self, loop=None):
        super(Fetcher, self).__init__(loop)
        self.urls = []
        for i in range(1, 5):
            for j in range(1, 6):
                self.urls.append(
                    'http://www.ip3366.net/free/?stype=%d&page=%d' % (i, j))

    @BaseFetcher.sleep(0.5)
    async def handle(self, resp):
        return re.findall(
            r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>',
            await resp.text())


if __name__ == '__main__':
    Fetcher.test()
