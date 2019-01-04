# -*- coding: utf-8 -*-
import random

from six import PY3

from db.DBClient import DBClient
from manager.ProxyFetcher import ProxyFetcher
from utils import LogHandler, Config
from utils import verify_proxy_format


class ProxyManager(object):
    """
    ProxyManager
    """
    log = LogHandler('proxy_manager')
    db = DBClient()

    def refresh(self):
        """
        fetch proxy into Db by ProxyGetter
        :return:
        """
        for fetcher in ProxyFetcher.find_fetchers():
            proxy_set = set()
            try:
                self.log.info("{func}: fetch proxy start".format(func=fetcher['name']))
                proxies = fetcher['func']()
            except Exception as e:
                self.log.error("{func}: fetch proxy fail".format(func=fetcher['name']))
                continue
            for proxy in proxies:
                proxy = proxy.strip()
                if proxy and verify_proxy_format(proxy):
                    self.log.info('{func}: fetch proxy {proxy}'.format(func=fetcher['name'], proxy=proxy))
                    proxy_set.add(proxy)
                else:
                    self.log.error('{func}: fetch proxy {proxy} error'.format(func=fetcher['name'], proxy=proxy))
            self.log.info('{func}: fetched {count} proxies'.format(func=fetcher['name'], count=len(proxy_set)))

            # store
            for proxy in proxy_set:
                self.db.change_table(Config.USABLE_PROXY)
                if self.db.exists(proxy):
                    continue
                self.db.change_table(Config.RAW_PROXY)
                self.db.put(proxy)

    def get(self):
        """
        return a useful proxy
        :return:
        """
        self.db.change_table(Config.USABLE_PROXY)
        item_dict = self.db.get_all()
        if item_dict:
            if PY3:
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
        self.db.change_table(Config.USABLE_PROXY)
        self.db.delete(proxy)

    def get_all(self):
        """
        get all proxy from pool as list
        :return:
        """
        self.db.change_table(Config.USABLE_PROXY)
        item_dict = self.db.get_all()
        if PY3:
            return list(item_dict.keys()) if item_dict else list()
        return item_dict.keys() if item_dict else list()

    def get_size(self):
        self.db.change_table(Config.RAW_PROXY)
        total_raw_proxy = self.db.get_size()
        self.db.change_table(Config.USABLE_PROXY)
        total_useful_queue = self.db.get_size()
        return {Config.RAW_PROXY: total_raw_proxy, Config.USABLE_PROXY: total_useful_queue}


if __name__ == '__main__':
    pp = ProxyManager()
    pp.refresh()
