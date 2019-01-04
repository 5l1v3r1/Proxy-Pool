# -*- coding: utf-8 -*-
import sys
from threading import Thread

sys.path.append('../')

from utils import valid_usable_proxy, Config
from manager.ProxyManager import ProxyManager
from utils import LogHandler

FAIL_COUNT = 1  # 校验失败次数， 超过次数删除代理


class ProxyCheck(Thread, ProxyManager):
    def __init__(self, queue, item_dict):
        Thread.__init__(self)
        self.log = LogHandler('proxy_check', file=False)  # 多线程同时写一个日志文件会有问题
        self.queue = queue
        self.item_dict = item_dict

    def run(self):
        self.db.change_table(Config.USABLE_PROXY)
        while self.queue.qsize():
            proxy = self.queue.get()
            count = self.item_dict[proxy]
            if valid_usable_proxy(proxy):
                # 验证通过计数器减1
                if count and int(count) > 0:
                    self.db.put(proxy, num=int(count) - 1)
                else:
                    pass
                self.log.info('ProxyCheck: {} validation pass'.format(proxy))
            else:
                self.log.info('ProxyCheck: {} validation fail'.format(proxy))
                if count and int(count) + 1 >= FAIL_COUNT:
                    self.log.info('ProxyCheck: {} fail too many, delete!'.format(proxy))
                    self.db.delete(proxy)
                else:
                    self.db.put(proxy, num=int(count) + 1)
            self.queue.task_done()
