# coding:utf-8
import re

import execjs
import gevent

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = '66ip'

    def __init__(self, tasks, result, pool=None):
        self.cookie = None
        super(Fetcher, self).__init__(tasks, result, pool)
        self.urls = [
            'http://www.66ip.cn/areaindex_35/1.html'
        ]

    def prepare(self):
        req = self._request('http://www.66ip.cn/')
        if req.status_code != 521:
            return
        html = req.text
        # 提取其中的JS加密函数
        js_func = ''.join(re.findall(r'(function .*?)</script>', html))

        # 提取其中执行JS函数的参数
        js_arg = re.findall(r'setTimeout\(\"(\S+)\((\d+)\)\"', html)[0]

        # 修改JS函数，使其返回Cookie内容
        js_func = js_func.replace('eval("qo=eval;qo(po);")', 'return po;')
        code = execjs.compile(js_func)

        # 执行JS获取Cookie
        cookie_str = code.call(js_arg[0], js_arg[1])
        cookie = re.findall(r"cookie='(\S+)", cookie_str)[0]
        if 'Set-Cookie' in req.headers:
            cookie += re.findall(r'^\S+', req.headers['Set-Cookie'])[0]
        # self.logger.info(cookie)
        self.headers['Cookie'] = cookie

    def handle(self, resp):
        return re.findall(r'(\d+\.\d+\.\d+\.\d+)[\S\s]+?(\d+)</td><td>', resp.text)


if __name__ == '__main__':
    Fetcher.test()
