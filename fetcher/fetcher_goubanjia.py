# coding:utf-8
import re

from fetcher import BaseFetcher
from utils.functions import IPPortPatternGlobal


class Fetcher(BaseFetcher):
    name = 'goubanjia'

    def __init__(self, loop=None):
        super(Fetcher, self).__init__(loop)
        self.urls = [
            'http://www.goubanjia.com/'
        ]

    async def handle(self, resp):
        html = re.sub(r"<p style='display:\s*none;'>\S*</p>", '',
                      await resp.text())
        html = re.sub(r'</?(span|div).*?>', '', html)
        return IPPortPatternGlobal.findall(html)


if __name__ == '__main__':
    Fetcher.test()
