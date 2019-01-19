# coding:utf-8
import gc
import time

import gevent

from manager import ProxyFetcherManager, ProxyManager
from model import ProxyModel
from utils import LogHandler
from verify.proxy_verifier import ProxyGeventVerifier

gevent.hub.Hub.NOT_ERROR = (Exception,)
logger = LogHandler('ProxyFetcherScheduler')


class ProxyFetcherScheduler:
    def __gen_fetch_tasks(self, tasks, result):
        start = time.time()
        for FetcherClass in ProxyFetcherManager.fetchers():
            if not FetcherClass.enabled:
                continue
            fetcher = FetcherClass(tasks, result)
            logger.info("Start Fetcher: %s" % fetcher)
            fetcher.fill_task()
        logger.debug('Using %.2f seconds to start fetchers' % (time.time() - start))

    def __wait_fetch(self, tasks):
        start = time.time()
        gevent.joinall(tasks)
        logger.debug('Using %.2f second to finish fetch processes' % (time.time() - start))

    def __gen_gevent_tasks(self, proxies):
        verifier = ProxyGeventVerifier()
        tasks = verifier.generate_tasks(proxies)
        logger.info('Created %d verify tasks' % len(proxies))
        return tasks

    def __wait_for_gevent_tasks(self, tasks):
        start = time.time()
        gevent.joinall(tasks)
        logger.info('Gevent Proxy Verify Using %d sec.' % (time.time() - start))

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
        pm.commit()
        logger.info('Added %d new usable proxy' % count_usable)

    def __remove_exist_proxies(self, pm, proxies):
        all_proxy = set()
        for i in pm.all_proxy():
            all_proxy.add('%s:%d' % (i.ip, i.port))
        result = []
        for i in proxies:
            if i not in all_proxy:
                result += [ProxyModel.from_url('%s://%s' % (j, i)) for j in ['http', 'https', 'socks5']]
        logger.info('Remove %d exist proxies' % (len(proxies) - len(result) / 3))
        return result

    def run(self):
        try:
            pm = ProxyManager()
            proxies = set()
            tasks = []
            self.__gen_fetch_tasks(tasks, proxies)
            self.__wait_fetch(tasks)
            logger.info('Fetched %d proxies' % len(proxies))
            proxies = self.__remove_exist_proxies(pm, proxies)
            if proxies:
                verify_tasks = self.__gen_gevent_tasks(proxies)
                self.__wait_for_gevent_tasks(verify_tasks)
                self.__write_verify_result(pm, proxies)
            pm.close()
            gc.collect()
            logger.info('ProxyModel Fetch Finished, wait for 10 min')
        except Exception as e:
            logger.exception(e)


if __name__ == '__main__':
    while True:
        ProxyFetcherScheduler().run()
        time.sleep(60 * 10)
