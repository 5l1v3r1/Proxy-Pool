# coding:utf-8
import asyncio
import time

import requests


@asyncio.coroutine
def main():
    loop = asyncio.get_event_loop()
    future1 = loop.run_in_executor(None, requests.get, 'http://httpbin.org/ip')
    future2 = loop.run_in_executor(None, requests.get, 'http://www.sina.com.cn')
    start = time.time()
    response1 = yield from future1
    print(time.time() - start)
    start = time.time()
    response2 = yield from future2
    print(time.time() - start)
    print(len(response1.text))
    print(len(response2.text))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
