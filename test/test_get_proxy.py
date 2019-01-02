# -*- coding: utf-8 -*-
import sys

sys.path.append('..')
from fetcher.ProxyFetcher import ProxyFetcher
from utils import Config


def test_get_proxy():
    """
    test class GetFreeProxy in fetcher.GetFreeProxy
    :return:
    """
    gc = Config()
    proxy_getter_functions = gc.proxy_getter_functions
    for proxyGetter in proxy_getter_functions:
        proxy_count = 0
        for proxy in getattr(ProxyFetcher, proxyGetter.strip())():
            if proxy:
                print('{func}: fetch proxy {proxy},proxy_count:{proxy_count}'.format(func=proxyGetter, proxy=proxy, proxy_count=proxy_count))
                proxy_count += 1
        # assert proxy_count >= 20, '{} fetch proxy fail'.format(proxyGetter)


if __name__ == '__main__':
    test_get_proxy()
