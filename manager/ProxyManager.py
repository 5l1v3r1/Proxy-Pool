# -*- coding: utf-8 -*-
import random

import six

from db.DBClient import DBClient
from fetcher.ProxyFetcher import ProxyFetcher
from utils import Config, Singleton
from utils import LogHandler
from utils import verify_proxy_format

RAW_PROXY = 'raw_proxy'
USABLE_PROXY = 'usable_proxy'


@six.add_metaclass(Singleton)
class ProxyManager(object):
    """
    ProxyManager
    """
    log = LogHandler('proxy_manager')
    db = DBClient()
    config = Config()

    def __init__(self):
        super(ProxyManager, self).__init__()

    def refresh(self):
        """
        fetch proxy into Db by ProxyGetter
        :return:
        """
        for proxyGetter in self.config.proxy_getter_functions:
            # fetch
            proxy_set = set()
            try:
                self.log.info("{func}: fetch proxy start".format(func=proxyGetter))
                proxy_iter = [_ for _ in getattr(ProxyFetcher, proxyGetter.strip())()]
            except Exception as e:
                self.log.error("{func}: fetch proxy fail".format(func=proxyGetter))
                continue
            for proxy in proxy_iter:
                proxy = proxy.strip()
                if proxy and verify_proxy_format(proxy):
                    self.log.info('{func}: fetch proxy {proxy}'.format(func=proxyGetter, proxy=proxy))
                    proxy_set.add(proxy)
                else:
                    self.log.error('{func}: fetch proxy {proxy} error'.format(func=proxyGetter, proxy=proxy))

            # store
            for proxy in proxy_set:
                self.db.change_table(self.useful_proxy_queue)
                if self.db.exists(proxy):
                    continue
                self.db.change_table(self.raw_proxy_queue)
                self.db.put(proxy)

    def get(self):
        """
        return a useful proxy
        :return:
        """
        self.db.change_table(self.useful_proxy_queue)
        item_dict = self.db.get_all()
        if item_dict:
            if six.PY3:
                return random.choice(list(item_dict.keys()))
            else:
                return random.choice(item_dict.keys())
        return None
        # return self.db.pop()

    def delete(self, proxy):
        """
        delete proxy from pool
        :param proxy:
        :return:
        """
        self.db.change_table(self.useful_proxy_queue)
        self.db.delete(proxy)

    def get_all(self):
        """
        get all proxy from pool as list
        :return:
        """
        self.db.change_table(self.useful_proxy_queue)
        item_dict = self.db.get_all()
        if six.PY3:
            return list(item_dict.keys()) if item_dict else list()
        return item_dict.keys() if item_dict else list()

    def get_size(self):
        self.db.change_table(self.raw_proxy_queue)
        total_raw_proxy = self.db.get_size()
        self.db.change_table(self.useful_proxy_queue)
        total_useful_queue = self.db.get_size()
        return {RAW_PROXY: total_raw_proxy, USABLE_PROXY: total_useful_queue}


if __name__ == '__main__':
    pp = ProxyManager()
    pp.refresh()
