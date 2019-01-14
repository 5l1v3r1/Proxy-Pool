# coding:utf-8
import asyncio
import time
from threading import Thread

from manager import ProxyManager, ProxyVerifier
from utils import LogHandler

logger = LogHandler('ProxyVerifyScheduler')


class ProxyVerifyScheduler(Thread):
    def __init__(self, loop=None):
        super(ProxyVerifyScheduler, self).__init__(name='ProxyVerifyScheduler')
        self.loop = loop or asyncio.get_event_loop()

    def run(self):
        proxy_manager = ProxyManager()
        while True:
            proxies = proxy_manager.proxy_verified_before(minutes=30)

            if not len(proxies):
                logger.info('Not proxy found! sleep 1 minutes.')
                time.sleep(60 * 1)
                continue
            logger.info("Start proxy verify")
            verifier = ProxyVerifier(self.loop)
            start = time.time()
            tasks = []
            for proxy in proxies:
                task = asyncio.ensure_future(verifier.verify(proxy))
                tasks.append(task)
            logger.info('Created %d verify tasks' % len(tasks))
            self.loop.run_until_complete(asyncio.wait(tasks))
            logger.info('Proxy Verify Using %d sec.' % (time.time() - start))
            for i in tasks:
                result = i.result()
                if result.usable:
                    proxy_manager.verify_passed(result)
                else:
                    proxy_manager.verify_failed(result)
            proxy_manager.commit()
            logger.info('Valid Complete! sleep 5 minutes.')


if __name__ == '__main__':
    ProxyVerifyScheduler().run()
