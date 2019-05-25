# coding:utf-8
import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scheduler.fetch_scheduler import fetch_proxy
from scheduler.verify_scheduler import verify_proxy


def run():
    loop = asyncio.get_event_loop()
    scheduler = AsyncIOScheduler()

    scheduler.add_job(fetch_proxy, 'interval', minutes=10,
                      next_run_time=datetime.now())
    scheduler.add_job(verify_proxy, 'interval', minutes=5,
                      next_run_time=datetime.now())
    scheduler.start()
    loop.run_forever()

if __name__ == '__main__':
    run()
