# coding:utf-8
import sys

sys.path.append('../')

from web.Application import run as WebService
from scheduler import ProxyFetcherScheduler, ProxyVerifyScheduler


def run():
    ts = [
        ProxyFetcherScheduler(),
        ProxyVerifyScheduler()
    ]

    for p in ts:
        p.setDaemon(True)
        p.start()
    WebService()


if __name__ == '__main__':
    run()
