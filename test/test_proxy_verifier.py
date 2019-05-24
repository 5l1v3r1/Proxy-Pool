# coding:utf-8
import asyncio
import time

from model import ProxyModel
from proxy_verifier import ProxyAsyncVerifier


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    start = time.time()
    proxy = ProxyModel.from_url('socks5://127.0.0.1:1080')
    task = asyncio.ensure_future(ProxyAsyncVerifier(loop).check(proxy))
    loop.run_until_complete(task)
    print(time.time() - start)
    print(task.result())
    print(proxy.usable)
