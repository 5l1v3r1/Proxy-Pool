# coding:utf-8
import re

import execjs
from requests import Response

from fetcher import IFetcher
from utils import WebRequest, random_user_agent


class Fetcher(IFetcher):
    name = '66ip'
    source = 'www.66ip.cn'
    cookie = None
    async = False
    user_agent = random_user_agent()

    def get_cookie(self, req: Response):
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
        self.cookie = cookie

    def fetch(self):
        urls = [
            'http://www.66ip.cn/areaindex_35/1.html'
        ]
        ret = []

        for url in urls:
            if self.cookie:
                req = WebRequest.get(url, header={'User-Agent': self.user_agent, 'Cookie': self.cookie}, retry_time=1)
            else:
                req = WebRequest.get(url, header={'User-Agent': self.user_agent}, retry_time=1)
            html = req.text
            if req.status_code == 521:
                self.get_cookie(req)
                if self.cookie:
                    html = WebRequest.get(url, retry_time=1, header={'User-Agent': self.user_agent, 'Cookie': self.cookie}).text
            matches = re.findall(r'(\d+\.\d+\.\d+\.\d+)[\S\s]+?(\d+)</td><td>', html)
            if not matches:
                continue
            for i in matches:
                ret.append(':'.join(i))
        ret = list(set(ret))
        return ret


if __name__ == '__main__':
    tasks = Fetcher().fetch()
    print(tasks)
