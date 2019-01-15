# coding:utf-8
import asyncio
import time
from threading import Thread

from manager import ProxyManager
from utils import LogHandler
from verify.proxy_verifier_asyncio import ProxyAsyncVerifier

logger = LogHandler('ProxyVerifyAsyncScheduler')


class ProxyVerifyAsyncScheduler(Thread):
    def __init__(self, loop=None):
        super(ProxyVerifyAsyncScheduler, self).__init__(name='ProxyVerifyAsyncScheduler')

    def run(self):
        proxy_manager = ProxyManager()
        loop = None
        while True:
            proxies = proxy_manager.proxy_verified_before(minutes=5, limit=1000)
            if not len(proxies):
                logger.info('Not proxy found! sleep 5 minutes.')
                time.sleep(60 * 5)
                continue
            logger.info("Start proxy verify")
            loop = loop or asyncio.new_event_loop()
            verifier = ProxyAsyncVerifier(loop)
            start = time.time()
            task = asyncio.ensure_future(verifier.verify_proxy(proxies), loop=loop)
            logger.info('Created %d verify tasks' % len(proxies))
            try:
                loop.run_until_complete(task)
            except Exception as e:
                loop.close()
                loop = None
                logger.exception(e)
                continue
            print(verifier.finished)
            logger.info('Proxy Verify Using %d sec.' % (time.time() - start))
            for proxy in proxies:
                if proxy.usable:
                    proxy_manager.verify_passed(proxy)
                else:
                    proxy_manager.verify_failed(proxy)
            proxy_manager.commit()
            logger.info('Valid Complete!')
            # loop.close()


if __name__ == '__main__':
    ProxyVerifyAsyncScheduler().run()
