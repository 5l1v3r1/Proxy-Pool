# coding:utf-8
import asyncio
import time

import gc

from manager.fetcher_manager import FetcherManager
from manager.proxy_manager import ProxyManager
from model import ProxyModel
from proxy_verifier import ProxyAsyncVerifier
from utils import Logger
from utils.functions import IPPortPatternLine
from utils.python import patch_win_selector

logger = Logger('ProxyFetcherScheduler')

patch_win_selector()


def __gen_fetch_tasks(loop):
    tasks = []
    start = time.time()
    for name, fetcher_class in FetcherManager().list().items():
        if not fetcher_class.enable:
            logger.warning('Ignore Fetcher ' + name)
            continue
        fetcher = fetcher_class(loop)
        logger.info("Fetch proxy with %s start" % name)
        tasks += fetcher.gen_tasks()
    logger.debug('Starting fetchers in %.2f sec.' % (time.time() - start))
    return tasks


def __get_result(tasks):
    result = set()
    for task in tasks:
        _task_result = task.result()
        if isinstance(_task_result, str):
            _task_result = [_task_result]
        if not isinstance(_task_result, list):
            logger.info('Unknown proxy list type:', type(_task_result))
        for i in _task_result:
            proxy = i.strip()
            if proxy and IPPortPatternLine.match(proxy):
                # logger.debug('Fetch proxy %s' % proxy)
                result.add(proxy)
            else:
                logger.error('Fetch proxy %s error' % proxy)

    return result


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


def __remove_exist_proxies(pm, proxies):
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


async def fetch_proxy(loop=None):
    loop = loop or asyncio.get_event_loop()
    fetch_tasks = __gen_fetch_tasks(loop)
    start = time.time()
    await asyncio.gather(*fetch_tasks)
    logger.debug('Using %.2f second to finish fetch processes' % (
            time.time() - start))
    proxies = __get_result(fetch_tasks)

    logger.info('Fetched %d proxies' % len(proxies))

    pm = ProxyManager()
    proxies = __remove_exist_proxies(pm, proxies)
    if proxies:
        logger.info("Start proxy verify")
        verifier = ProxyAsyncVerifier(loop)
        verify_tasks = verifier.verify(proxies)
        start = time.time()
        await asyncio.gather(*verify_tasks)
        logger.info('Proxy Verify Using %d sec.' % (time.time() - start))
        __write_verify_result(pm, proxies)
    else:
        logger.info('No Proxy Found!')
    pm.commit()
    pm.close()
    gc.collect()


if __name__ == '__main__':
    while True:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.ensure_future(fetch_proxy(loop)))
        logger.info('Proxy Fetch Finished, wait for 10 min')
        time.sleep(60 * 10)
