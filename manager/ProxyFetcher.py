# -*- coding: utf-8 -*-
import imp
import inspect
import os
from glob import glob

from fetcher import IFetcher
from utils import Config


class ProxyFetcher(object):
    """
    proxy getter
    """

    @classmethod
    def _find_fetcher_class(cls, fetcher):
        for (name, klass) in inspect.getmembers(fetcher, inspect.isclass):
            if issubclass(klass, IFetcher) and klass != IFetcher:
                return klass
        raise Exception("Failed to locate Plugin class in " + fetcher)

    @classmethod
    def find_fetchers(cls):
        ret = []
        for fetcher_path in glob(os.path.join(Config.project_dir, 'fetcher', 'fetcher_*.py')):
            fetcher_name = os.path.basename(fetcher_path)[:-3]
            fetcher = imp.load_source(fetcher_name, fetcher_path).Fetcher()
            ret.append({
                'name': fetcher.name,
                'source': fetcher.source,
                'enabled': fetcher.enabled,
                'func': fetcher.fetch
            })
        return ret


if __name__ == '__main__':
    print(ProxyFetcher.find_fetchers())
    # from manager.CheckProxy import CheckProxy
    # CheckProxy.checkAllGetProxyFunc()
