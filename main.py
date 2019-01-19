# coding:utf-8
from datetime import datetime

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from gevent.monkey import patch_all

patch_all()
from web.app import run as WebService
from scheduler import ProxyFetcherScheduler, ProxyVerifyGeventScheduler
from apscheduler.schedulers.background import BackgroundScheduler


def run():
    scheduler = BackgroundScheduler()

    scheduler.add_job(ProxyFetcherScheduler().run, 'interval', minutes=10, next_run_time=datetime.now())
    scheduler.add_job(ProxyVerifyGeventScheduler().run, 'interval', minutes=5, next_run_time=datetime.now())
    scheduler.start()
    WebService()


if __name__ == '__main__':
    run()
