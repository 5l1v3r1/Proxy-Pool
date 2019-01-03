# -*- coding: utf-8 -*-
import sys

sys.path.append('../')

from api.ProxyApi import run as ProxyApiRun
from scheduler import ProxyCheckScheduler, ProxyRefreshScheduler, ProxyFetcherScheduler


def run():
    ts = [
        ProxyFetcherScheduler(),
        ProxyCheckScheduler(),
        ProxyRefreshScheduler()
    ]

    for p in ts:
        p.setDaemon(True)
        p.start()
    ProxyApiRun()
    for p in ts:
        p.join()


if __name__ == '__main__':
    run()
