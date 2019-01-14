# coding:utf-8
import asyncio
import re

from fetcher import IFetcher
from utils import WebRequest


class Fetcher(IFetcher):
    name = 'ip3366'
    source = 'www.ip3366.net'
    async = True

    async def parse(self, url):
        loop = asyncio.get_event_loop()
        req = lambda url: WebRequest.get(url, retry_time=1)
        try:
            r = await loop.run_in_executor(None, req, url)
        except Exception as e:
            return []
        ret = []
        proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
        for proxy in proxies:
            ret.append(":".join(proxy))
        return ret

    def fetch(self):
        url = 'http://www.ip3366.net/free/?stype=%d&page=%d'
        tasks = []
        for x in range(1, 5):
            for y in range(1, 6):
                tasks.append(asyncio.ensure_future(self.parse(url % (x, y))))
        return tasks


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = Fetcher().fetch()
    loop.run_until_complete(asyncio.wait(tasks))
    for i in tasks:
        print(i.result())
