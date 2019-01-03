# -*- coding: utf-8 -*-
import logging
import time
from threading import Thread

from manager.ProxyManager import ProxyManager
from utils import LogHandler

logging.basicConfig()


class ProxyFetcherScheduler(ProxyManager, Thread):
    """
    代理定时刷新
    """

    def __init__(self):
        super(ProxyFetcherScheduler, self).__init__()
        Thread.__init__(self)
        self.name = 'ProxyRefreshScheduler'
        self.log = LogHandler('refresh_schedule')

    def run(self):
        while True:
            self.refresh()
            time.sleep(60 * 10)


if __name__ == '__main__':
    ProxyFetcherScheduler().run()
