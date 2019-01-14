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
    def add_result_set(s: set, l):
        if isinstance(l, str):
            l = [l]
        if not isinstance(l, list):
            logger.info('Unknown proxy list type:', type(l))
        for i in l:
            proxy = i.strip()
            if proxy and verify_proxy_format(proxy):
                # logger.debug('Fetch proxy %s' % proxy)
                s.add(proxy)
            else:
                logger.error('Fetch proxy %s error' % proxy)

    async def fetch(self, func):  # convert sync function to async's
        ret = await self.loop.run_in_executor(None, func)
        return ret

    def __gen_fetch_tasks(self, result_set: set):
        tasks = []
        start = time.time()
        for fetcher in ProxyFetcherManager.fetchers():
            if not fetcher.enabled:
                continue
            logger.info("Fetch proxy with %s start" % fetcher)
            if fetcher.async:
                for i in fetcher.fetch():
                    if isinstance(i, Task):
                        tasks.append(i)
                    else:
                        self.add_result_set(result_set, i)
            else:
                tasks.append(asyncio.ensure_future(self.fetch(fetcher.fetch)))
        logger.debug('Using %.2f seconds to start fetchers' % (time.time() - start))
        return tasks

    def __wait_fetch(self, tasks):
        start = time.time()
        self.loop.run_until_complete(asyncio.wait(tasks))
        logger.debug('Using %.2f second to finish fetch processes' % (time.time() - start))

    def __generate_result(self, tasks, result_set):
        for task in tasks:
            for i in task.result():
                self.add_result_set(result_set, i)
        logger.info('Fetched %d proxies' % len(result_set))

    def __gen_verify_tasks(self, result_set):
        logger.info("Start proxy verify")
        verifier = ProxyVerifier(self.loop)
        tasks = []
        for i in result_set:
            tasks += verifier.gen_tasks(i)
        return tasks

    def __wait_for_verify(self, tasks):
        start = time.time()
        self.loop.run_until_complete(asyncio.wait(tasks))
        logger.info('Proxy Verify Using %d sec.' % (time.time() - start))

    def __write_verify_result(self, tasks):
        pm = ProxyManager()
        for i in tasks:
            result = i.result()
            pm.add_proxy(result)

    def run(self):

        while True:
            result_set = set()
            fetch_tasks = self.__gen_fetch_tasks(result_set)
            self.__wait_fetch(fetch_tasks)
            self.__generate_result(fetch_tasks, result_set)
            verify_tasks = self.__gen_verify_tasks(result_set)
            self.__wait_for_verify(verify_tasks)
            self.__write_verify_result(verify_tasks)

            logger.info('ProxyModel Fetch Finished, wait for 10 min')
            time.sleep(60 * 10)


if __name__ == '__main__':
    ProxyFetcherScheduler().run()
