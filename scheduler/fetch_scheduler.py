# coding:utf-8
import asyncio
import time
from threading import Thread

import gc

from manager.proxy_manager import ProxyManager
from manager.fetcher_manager import FetcherManager
from model import ProxyModel
from utils import Logger
from utils.functions import IPPortPatternLine
from utils.python import patch_win_selector
from proxy_verifier import ProxyAsyncVerifier

logger = Logger('ProxyFetcherScheduler')

patch_win_selector()


def merge_result(s, l):
    if isinstance(l, str):
        l = [l]
    if not isinstance(l, list):
        logger.info('Unknown proxy list type:', type(l))
    for i in l:
        proxy = i.strip()
        if proxy and IPPortPatternLine.match(proxy):
            # logger.debug('Fetch proxy %s' % proxy)
            s.add(proxy)
        else:
            logger.error('Fetch proxy %s error' % proxy)


class ProxyFetcherScheduler(Thread):
    def __init__(self, loop=None):
        super(ProxyFetcherScheduler, self).__init__(
            name='ProxyFetcherScheduler')
        self.loop = loop or asyncio.get_event_loop()

    def __gen_fetch_tasks(self):
        tasks = []
        start = time.time()
        for name, fetcher_class in FetcherManager().list().items():
            if not fetcher_class.enable:
                logger.warning('Ignore Fetcher ' + name)
                continue
            fetcher = fetcher_class(self.loop)
            logger.info("Fetch proxy with %s start" % name)
            tasks += fetcher.gen_tasks()
        logger.debug(
            'Using %.2f seconds to start fetchers' % (time.time() - start))
        return tasks

    def __wait_fetch(self, tasks):
        start = time.time()
        self.loop.run_until_complete(asyncio.gather(*tasks))
        logger.debug('Using %.2f second to finish fetch processes' % (
                time.time() - start))

    def __get_result(self, tasks):
        result = set()
        for task in tasks:
            merge_result(result, task.result())
        return result

    def __wait_for_verify(self, tasks):
        start = time.time()
        self.loop.run_until_complete(asyncio.gather(*tasks))
        logger.info('Proxy Verify Using %d sec.' % (time.time() - start))

    @staticmethod
    def __write_verify_result(pm, proxies):
        all_iploc = set()
        for i in pm.all_iploc():
            all_iploc.add(i.ip)
        count_usable = 0
        for i in proxies:
            if not i.usable:
                continue
            if i.ip not in all_iploc:
                pm.add_iploc_no_check(i.ip)
                all_iploc.add(i.ip)
            pm.add_proxy_no_check(i)
            count_usable += 1
        logger.info('Added %d new usable proxy' % count_usable)

    def __remove_exist_proxies(self, pm, proxies):
        all_proxy = set()
        for i in pm.all_proxy():
            all_proxy.add('%s:%d' % (i.ip, i.port))
        result = []
        for i in proxies:
            if i not in all_proxy:
                result += [ProxyModel.from_url('%s://%s' % (j, i)) for j in
                           ['http', 'https', 'socks5']]
        logger.info(
            'Remove %d exist proxies' % (len(proxies) - len(result) / 3))
        return result

    def run(self):
        fetch_tasks = self.__gen_fetch_tasks()
        self.__wait_fetch(fetch_tasks)
        proxies = self.__get_result(fetch_tasks)
        logger.info('Fetched %d proxies' % len(proxies))

        pm = ProxyManager()
        proxies = self.__remove_exist_proxies(pm, proxies)
        if proxies:
            logger.info("Start proxy verify")
            verifier = ProxyAsyncVerifier(self.loop)
            verify_tasks = verifier.verify(proxies)
            self.__wait_for_verify(verify_tasks)
            self.__write_verify_result(pm, proxies)
        pm.commit()
        gc.collect()


if __name__ == '__main__':
    while True:
        ProxyFetcherScheduler().run()
        logger.info('ProxyModel Fetch Finished, wait for 10 min')
        time.sleep(60 * 10)
