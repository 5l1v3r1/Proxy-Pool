# -*- coding: utf-8 -*-
import sys
import threading
from multiprocessing import Process

sys.path.append('../')

from api.ProxyApi import run as ProxyApiRun
from scheduler.ProxyCheckScheduler import ProxyCheckScheduler
from scheduler.ProxyRefreshScheduler import ProxyRefreshScheduler


def run():
    p_list = list()
    p1 = ProxyCheckScheduler()
    p_list.append(p1)
    p2 = ProxyRefreshScheduler()
    p_list.append(p2)

    for p in p_list:
        p.daemon = True
        p.start()
    ProxyApiRun()
    for p in p_list:
        p.join()


if __name__ == '__main__':
    run()
