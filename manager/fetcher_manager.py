# coding:utf-8
import imp
import inspect
import os
from glob import glob

from fetcher import IFetcher
from utils import Config


class ProxyFetcherManager(object):
    @classmethod
    def _find_fetcher_class(cls, fetcher):
        for (name, klass) in inspect.getmembers(fetcher, inspect.isclass):
            if issubclass(klass, IFetcher) and klass != IFetcher:
                return klass
        raise Exception("Failed to locate Plugin class in " + fetcher)

    @staticmethod
    def fetchers():
        ret = []
        for fetcher_path in glob(os.path.join(Config.PROJECT_DIR, 'fetcher', 'fetcher_*.py')):
            fetcher_name = os.path.basename(fetcher_path)[:-3]
            fetcher = imp.load_source(fetcher_name, fetcher_path).Fetcher()
            ret.append(fetcher)
        return ret


if __name__ == '__main__':
    print(ProxyFetcherManager.fetchers())
    # from manager import CheckProxy
    # CheckProxy.checkAllGetProxyFunc()
