# coding:utf-8
import time

import gevent

from manager import ProxyManager
from utils import LogHandler
from verify.proxy_verifier import ProxyGeventVerifier

logger = LogHandler('ProxyVerifyGeventScheduler')


class ProxyVerifyGeventScheduler:
    def run(self):
        try:
            proxy_manager = ProxyManager()
            logger.info("Start proxy verify")
            while True:
                proxies = proxy_manager.proxy_verified_before(minutes=30, limit=1000)
                if not len(proxies):
                    logger.info('Not proxy need to be verified! Sleep [ 5 ] minutes.')
                    proxy_manager.close()
                    break
                verifier = ProxyGeventVerifier()
                start = time.time()
                tasks = verifier.generate_tasks(proxies)
                logger.info('Created %d verify tasks' % len(proxies))
                gevent.joinall(tasks)
                logger.info('Proxy Verify Using %d sec.' % (time.time() - start))
                passed, failed = 0, 0
                for proxy in proxies:
                    if proxy.usable:
                        passed += 1
                        proxy_manager.verify_passed(proxy)
                    else:
                        failed += 1
                        proxy_manager.verify_failed(proxy)
                proxy_manager.commit()
                logger.info('Valid Complete! %d / %d' % (passed, failed))
                proxy_manager.remove_bad_proxy()
        except Exception as e:
            logger.exception(e)


if __name__ == '__main__':
    ProxyVerifyGeventScheduler().run()
