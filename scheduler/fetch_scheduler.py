# coding:utf-8
import asyncio
import time
from asyncio import Task
from threading import Thread

from manager import ProxyFetcherManager, ProxyManager, ProxyVerifier
from utils import LogHandler, verify_proxy_format

logger = LogHandler('ProxyFetcherScheduler')


class ProxyFetcherScheduler(Thread):
    def __init__(self, loop=None):
        super(ProxyFetcherScheduler, self).__init__(name='ProxyFetcherScheduler')
        self.loop = loop or asyncio.get_event_loop()

    @staticmethod
    def add_proxy_set(s: set, i):
        proxy = i.strip()
        if proxy and verify_proxy_format(proxy):
            # logger.debug('Fetch proxy %s' % proxy)
            s.add(proxy)
        else:
            logger.error('Fetch proxy %s error' % proxy)

    async def fetch(self, func):  # convert sync function to async's
        ret = await self.loop.run_in_executor(None, func)
        return ret

    def run(self):
        pm = ProxyManager()
        while True:
            proxy_set = set()
            tasks = []
            for fetcher in ProxyFetcherManager.fetchers():
                logger.info("Fetch proxy with [ %s ] start" % fetcher['name'])
                for i in fetcher['func']():
                    if isinstance(i, Task):
                        tasks.append(i)
                    else:
                        self.add_proxy_set(proxy_set, i)
            self.loop.run_until_complete(asyncio.wait(tasks))
            for task in tasks:
                for i in task.result():
                    proxy_set.add(i)
            logger.info('Fetched %d proxies' % len(proxy_set))

            logger.info("Start proxy storage")
            verifier = ProxyVerifier(self.loop)
            start = time.time()
            tasks = []
            for i in proxy_set:
                tasks += verifier.verify_all(i)
            self.loop.run_until_complete(asyncio.wait(tasks))
            logger.info('Proxy Verify Using %d sec.' % (time.time() - start))
            for i in tasks:
                result = i.result()
                pm.add_proxy(result)

            logger.info('ProxyModel Fetch Finished, wait for 10 min')
            time.sleep(60 * 10)


if __name__ == '__main__':
    ProxyFetcherScheduler().run()
