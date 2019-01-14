# coding:utf-8
import asyncio
import re
import time

from fetcher import IFetcher
from utils import WebRequest


class Fetcher(IFetcher):
    name = '快代理'
    source = 'www.kuaidaili.com'
    last = None
    async = True

    async def parse(self, url):
        loop = asyncio.get_event_loop()
        while True:
            if not self.last or time.time() - self.last > 2:
                req = lambda url: WebRequest.get(url, retry_time=1)
                self.last = time.time()
                break
            else:
                time.sleep(0.5)
        try:
            r = await loop.run_in_executor(None, req, url)
        except Exception as e:
            return []
        ret = []
        proxies = re.findall(r'<td data-title="IP">(\S+)</td>\s+<td data-title="PORT">(\d+)</td>', r.text)
        for proxy in proxies:
            ret.append(':'.join(proxy))
        return ret

    def fetch(self):
        urls = ['https://www.kuaidaili.com/free/inha/%d/' % i for i in range(1, 6)] + \
               ['https://www.kuaidaili.com/free/intr/%d/' % i for i in range(1, 6)]
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
