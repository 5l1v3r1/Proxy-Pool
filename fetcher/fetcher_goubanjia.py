# coding:utf-8
import asyncio
import re

from fetcher import IFetcher
from utils import WebRequest


class Fetcher(IFetcher):
    name = 'goubanjia'
    source = 'www.goubanjia.com'
    async = True

    async def parse(self, url):
        loop = asyncio.get_event_loop()
        req = lambda url: WebRequest.get(url, retry_time=1)
        try:
            r = await loop.run_in_executor(None, req, url)
        except Exception as e:
            return []
        ret = []
        html = re.sub(r"<p style='display:\s*none;'>\S*</p>", '', r.text)
        html = re.sub(r'</?(span|div).*?>', '', html)
        for i in re.findall(r'(\d+\.\d+\.\d+\.\d+):(\d+)', html):
            ret.append(':'.join(i))
        return ret

    def fetch(self):
        urls = [
            'http://www.goubanjia.com/'
        ]
        tasks = []
        for url in urls:
            tasks.append(asyncio.ensure_future(self.parse(url)))
        return tasks


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = Fetcher().fetch()
    loop.run_until_complete(asyncio.wait(tasks))
    for i in tasks:
        print(i.result())
