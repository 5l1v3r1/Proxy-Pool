# coding:utf-8
import asyncio
import time

import gc

from manager.proxy_manager import ProxyManager
from proxy_verifier import ProxyAsyncVerifier
from utils import Logger
from utils.python import patch_win_selector

logger = Logger('ProxyVerifyAsyncScheduler')

patch_win_selector()


async def verify_proxy(loop=None):
    loop = loop or asyncio.get_event_loop()
    pm = ProxyManager()
    verifier = ProxyAsyncVerifier(loop)
    proxies = pm.proxy_verified_before(minutes=30, limit=1000)
    if not len(proxies):
        logger.info('Not proxy needs verify!')
        return
    logger.info("Start proxy verify")
    start = time.time()
    tasks = verifier.verify(proxies)
    logger.info('Created %d verify tasks' % len(proxies))
    await asyncio.gather(*tasks)
    logger.info('Proxy Verify Using %d sec.' % (time.time() - start))
    passed, failed = 0, 0
    for proxy in proxies:
        if proxy.usable:
            passed += 1
            pm.verify_passed(proxy)
        else:
            failed += 1
            pm.verify_failed(proxy)
    pm.commit()
    pm.remove_bad_proxy()
    logger.info('Valid Complete! %d / %d' % (passed, failed))
    pm.close()
    gc.collect()


if __name__ == '__main__':
    while True:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(verify_proxy(loop))
        logger.info('Sleep for 5 minutes')
        time.sleep(60 * 5)
