# -*- coding: utf-8 -*-
import sys
import time
from threading import Thread

from six.moves import queue

sys.path.append('../')

from scheduler.ProxyCheck import ProxyCheck
from manager.ProxyManager import ProxyManager


class ProxyCheckScheduler(ProxyManager, Thread):
    def __init__(self):
        super(ProxyCheckScheduler, self).__init__()
        Thread.__init__(self)
        self.name = 'ProxyCheckScheduler'
        self.queue = queue.Queue()
        self.proxy_item = dict()

    def __valid_proxy(self, threads=10):
        """
        验证useful_proxy代理
        :param threads: 线程数
        :return:
        """
        thread_list = list()
        for index in range(threads):
            thread_list.append(ProxyCheck(self.queue, self.proxy_item))

        for thread in thread_list:
            thread.daemon = True
            thread.start()

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
        self.db.change_table(self.useful_proxy_queue)
        self.proxy_item = self.db.get_all()
        for item in self.proxy_item:
            self.queue.put(item)


if __name__ == '__main__':
    p = ProxyCheckScheduler()
    p.main()
