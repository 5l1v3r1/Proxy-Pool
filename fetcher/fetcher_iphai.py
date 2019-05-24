# coding:utf-8
import re

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = 'IPHai'

    def __init__(self, loop=None):
        super(Fetcher, self).__init__(loop)
        self.urls = [
            'http://www.iphai.com/free/ng',
            'http://www.iphai.com/free/wg',
            'http://www.iphai.com/free/np',
            'http://www.iphai.com/free/wp',
            'http://www.iphai.com/'
        ]

    async def handle(self, resp):
        return re.findall(
            r'<td>\s*(\d+\.\d+\.\d+\.\d+)\s*</td>\s*<td>\s*(\d+)\s*</td>',
            await resp.text())


if __name__ == '__main__':
    Fetcher.test()
