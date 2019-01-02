# -*- coding: utf-8 -*-
import logging
import sys
import time
from threading import Thread

from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append('../')

from utils import valid_usable_proxy
from manager.ProxyManager import ProxyManager
from utils import LogHandler

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
        验证raw_proxy_queue中的代理, 将可用的代理放入useful_proxy_queue
        :return:
        """
        self.db.change_table(self.raw_proxy_queue)
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
                self.db.change_table(self.useful_proxy_queue)
                self.db.put(raw_proxy)
                self.log.info('ProxyRefreshScheduler: %s validation pass' % raw_proxy)
            else:
                self.log.info('ProxyRefreshScheduler: %s validation fail' % raw_proxy)
            self.db.change_table(self.raw_proxy_queue)
            raw_proxy_item = self.db.pop()
            remaining_proxies = self.get_all()
        self.log.info('ProxyRefreshScheduler: %s validProxy complete' % time.ctime())

    def run(self):
        self.validProxy()


def main(process_num=30):
    p = ProxyRefreshScheduler()

    # 获取新代理
    p.refresh()

    # 检验新代理
    pl = []
    for num in range(process_num):
        proc = ProxyRefreshScheduler()
        pl.append(proc)

    for num in range(process_num):
        pl[num].daemon = True
        pl[num].start()

    for num in range(process_num):
        pl[num].join()


def run():
    main()
    sch = BlockingScheduler()
    sch.add_job(main, 'interval', minutes=10)  # 每10分钟抓取一次
    sch.start()


if __name__ == '__main__':
    run()
