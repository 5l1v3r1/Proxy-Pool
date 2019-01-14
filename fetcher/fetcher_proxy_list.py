# coding:utf-8
import asyncio
import base64
import re

from fetcher import IFetcher
from utils import WebRequest, Config


class Fetcher(IFetcher):
    name = 'proxy-list'
    source = 'proxy-list.org'
    async = True

    async def parse(self, url):
        loop = asyncio.get_event_loop()
        req = lambda url: WebRequest.get(url, proxies={'https': 'https://' + Config.proxy})
        try:
            r = await loop.run_in_executor(None, req, url)
        except Exception as e:
            return []
        ret = []
        proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
        for proxy in proxies:
            ret.append(base64.b64decode(proxy).decode())
        return ret

    def fetch(self):
        if not Config.proxy:
            return
        urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
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
