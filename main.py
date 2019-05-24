# coding:utf-8
from scheduler.fetch_scheduler import ProxyFetcherScheduler
from scheduler.verify_scheduler import ProxyVerifyAsyncScheduler
from datetime import datetime

from web.app import run as WebService
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def run():
    scheduler = AsyncIOScheduler()
    fetcher = ProxyFetcherScheduler()
    verifier = ProxyVerifyAsyncScheduler()

    scheduler.add_job(fetcher.run, 'interval', minutes=10,
                      next_run_time=datetime.now())
    scheduler.add_job(verifier.run, 'interval', minutes=5,
                      next_run_time=datetime.now())
    scheduler.start()
    WebService()


if __name__ == '__main__':
    run()
