# coding:utf-8
import asyncio
import re

from fetcher import IFetcher
from utils import WebRequest, Config


class Fetcher(IFetcher):
    name = 'CN_PROXY'
    source = 'cn-proxy.com'
    async = True

    async def parse(self, url):
        loop = asyncio.get_event_loop()
        req = lambda url: WebRequest.get(url, proxies={'https': 'https://' + Config.proxy})
        try:
            r = await loop.run_in_executor(None, req, url)
        except Exception as e:
            return []
        ret = []
        proxies = re.findall(r'((?:\d{1,3}\.){3}\d{1,3})</td>\s*<td>(\d+)</td>', r.text)
        for proxy in proxies:
            ret.append(':'.join(proxy))
        return ret

    def fetch(self):
        urls = [
            'https://cn-proxy.com',
            'https://cn-proxy.com/archives/218'
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
