# -*- coding: utf-8 -*-
import time
from threading import Thread

from six.moves import queue

from manager.ProxyManager import ProxyManager
from scheduler.ProxyCheck import ProxyCheck
from utils import Config


class ProxyCheckScheduler(Thread, ProxyManager):
    def __init__(self):
        Thread.__init__(self)
        self.name = 'ProxyCheckScheduler'
        self.queue = queue.Queue()
        self.proxy_item = dict()

    def __valid_proxy(self):
        """
        验证usable_proxy代理
        :param threads: 线程数
        :return:
        """
        thread_list = []
        for index in range(10):
            thread = ProxyCheck(self.queue, self.proxy_item)
            thread.setDaemon(True)
            thread.start()
            thread_list.append(thread)

        for thread in thread_list:
            thread.join()

    def run(self):
        self.putQueue()
        while True:
            if not self.queue.empty():
                self.log.info("Start valid useful proxy")
                self.__valid_proxy()
            else:
                self.log.info('Valid Complete! sleep 5 minutes.')
                time.sleep(60 * 5)
                self.putQueue()

    def putQueue(self):
        self.db.change_table(Config.USABLE_PROXY)
        self.proxy_item = self.db.get_all()
        for item in self.proxy_item:
            self.queue.put(item)


if __name__ == '__main__':
    p = ProxyCheckScheduler()
    p.run()
