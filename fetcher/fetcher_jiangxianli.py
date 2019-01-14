# coding:utf-8
import asyncio
import re

from fetcher import IFetcher
from utils import WebRequest


class Fetcher(IFetcher):
    name = 'jiangxianli'
    source = 'www.jiangxianli.com'
    async = True

    async def parse(self, url):
        loop = asyncio.get_event_loop()
        req = lambda url: WebRequest.get(url, retry_time=1)
        try:
            r = await loop.run_in_executor(None, req, url)
        except Exception as e:
            return []
        ret = []
        proxies = re.findall(r'(?:\d{1,3}\.){3}\d{1,3}:\d+', r.text)
        for proxy in proxies:
            ret.append(proxy)
        return ret

    def fetch(self):
        urls = ['http://ip.jiangxianli.com/?page=%d' % i for i in range(1, 5)]
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
