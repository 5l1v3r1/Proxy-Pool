# coding:utf-8
import asyncio
import time

from manager.proxy_verifier import ProxyVerifier


def print_result(tasks):
    for i in tasks:
        _r = i.result()
        if _r.usable:
            print(_r)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    start = time.time()
    tasks = []
    tasks += ProxyVerifier(loop, '183.240.196.81').verify_all('118.25.231.155:1080')
    loop.run_until_complete(asyncio.wait(tasks))
    print(time.time() - start)
    print_result(tasks)
