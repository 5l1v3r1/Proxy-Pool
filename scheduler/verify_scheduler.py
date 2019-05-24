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


class ProxyVerifyAsyncScheduler:
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()

    def run(self):
        pm = ProxyManager()
        verifier = ProxyAsyncVerifier(self.loop)
        proxies = pm.proxy_verified_before(minutes=30, limit=1000)
        if not len(proxies):
            logger.info('Not proxy needs verify! Sleep [5] minutes.')
            return
        logger.info("Start proxy verify")
        start = time.time()
        tasks = asyncio.gather(*verifier.verify(proxies))
        logger.info('Created %d verify tasks' % len(proxies))
        self.loop.run_until_complete(tasks)
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
        logger.info('Valid Complete! %d / %d' % (passed, failed))
        pm.remove_bad_proxy()
        pm.close()
        gc.collect()


if __name__ == '__main__':
    while True:
        ProxyVerifyAsyncScheduler().run()
        time.sleep(60 * 5)
