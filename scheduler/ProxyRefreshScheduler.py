# -*- coding: utf-8 -*-
import logging
import time
from threading import Thread

from manager.ProxyManager import ProxyManager
from utils import LogHandler
from utils import valid_usable_proxy

logging.basicConfig()


class ProxyRefreshScheduler(ProxyManager, Thread):
    """
    代理定时刷新
    """

    def __init__(self):
        super(ProxyRefreshScheduler, self).__init__()
        Thread.__init__(self)
        self.name = 'ProxyRefreshScheduler'
        self.log = LogHandler('refresh_schedule')

    def validProxy(self):
        """
        验证RAW_PROXY中的代理, 将可用的代理放入USABLE_PROXY
        :return:
        """
        self.db.change_table(self.RAW_PROXY)
        raw_proxy_item = self.db.pop()
        self.log.info('ProxyRefreshScheduler: %s start validProxy' % time.ctime())
        # 计算剩余代理，用来减少重复计算
        remaining_proxies = self.get_all()
        while raw_proxy_item:
            raw_proxy = raw_proxy_item.get('proxy')
            if isinstance(raw_proxy, bytes):
                # 兼容Py3
                raw_proxy = raw_proxy.decode('utf8')

            if (raw_proxy not in remaining_proxies) and valid_usable_proxy(raw_proxy):
                self.db.change_table(self.USABLE_PROXY)
                self.db.put(raw_proxy)
                self.log.info('ProxyRefreshScheduler: %s validation pass' % raw_proxy)
            else:
                self.log.info('ProxyRefreshScheduler: %s validation fail' % raw_proxy)
            self.db.change_table(self.RAW_PROXY)
            raw_proxy_item = self.db.pop()
            remaining_proxies = self.get_all()
        self.log.info('ProxyRefreshScheduler: %s validProxy complete' % time.ctime())

    def batchRefresh(self, process_num=30):
        p = ProxyRefreshScheduler()

        # 获取新代理
        p.refresh()

        # 检验新代理
        ts = []
        for num in range(process_num):
            proc = Thread(target=self.validProxy)
            proc.setDaemon(True)
            proc.start()
            ts.append(proc)

        for t in ts:
            t.join()

    def run(self):
        while True:
            self.batchRefresh()
            time.sleep(60 * 1)


if __name__ == '__main__':
    ProxyRefreshScheduler().run()
