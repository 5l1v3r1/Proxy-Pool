# -*- coding: utf-8 -*-
import sys

from ProxyFetcher import GetFreeProxy

from utils import verify_proxy_format

sys.path.append('../')

from utils import LogHandler

log = LogHandler('check_proxy', file=False)


class CheckProxy(object):

    @staticmethod
    def checkAllGetProxyFunc():
        """
        检查ProxyFetcher所有代理获取函数运行情况
        Returns:
            None
        """
        import inspect
        member_list = inspect.getmembers(GetFreeProxy, predicate=inspect.isfunction)
        proxy_count_dict = dict()
        for func_name, func in member_list:
            log.info(u"开始运行 {}".format(func_name))
            try:
                proxy_list = [_ for _ in func() if verify_proxy_format(_)]
                proxy_count_dict[func_name] = len(proxy_list)
            except Exception as e:
                log.info(u"代理获取函数 {} 运行出错!".format(func_name))
                log.error(str(e))
        log.info(u"所有函数运行完毕 " + "***" * 5)
        for func_name, func in member_list:
            log.info(u"函数 {n}, 获取到代理数: {c}".format(n=func_name, c=proxy_count_dict.get(func_name, 0)))

    @staticmethod
    def checkGetProxyFunc(func):
        """
        检查指定的ProxyFetcher某个function运行情况
        Args:
            func: ProxyFetcher中某个可调用方法

        Returns:
            None
        """
        func_name = getattr(func, '__name__', "None")
        log.info("start running func: {}".format(func_name))
        count = 0
        for proxy in func():
            if verify_proxy_format(proxy):
                log.info("fetch proxy: {}".format(proxy))
                count += 1
        log.info("{n} completed, fetch proxy number: {c}".format(n=func_name, c=count))


if __name__ == '__main__':
    CheckProxy.checkAllGetProxyFunc()
    CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyFirst)
