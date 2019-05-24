# coding:utf-8
import re

import requests

from fetcher import BaseFetcher


class Fetcher(BaseFetcher):
    name = '66ip'
    enable = False

    def __init__(self, loop=None):
        self.cookie = None
        super(Fetcher, self).__init__(loop)
        self.urls = [
            'http://www.66ip.cn/areaindex_35/1.html'
        ]

    def prepare(self):
        import execjs
        resp = requests.get('http://www.66ip.cn/', headers=self.headers)
        if resp.status_code != 521:
            return
        html = resp.text()
        # 提取其中的JS加密函数
        js_func = ''.join(re.findall(r'<script>(.+?)</script>', html))
        print(js_func)
        js_func = js_func[:js_func.rfind('while(z++)')] \
                  + r'decode=function(){return y.replace(/\b\w+\b/g,function(y){return x[f(y,z)-1]||("_"+y)})};'
        print(js_func)
        js_func = execjs.compile(js_func).call('decode')
        print(js_func)
        # 提取其中执行JS函数的参数
        js_arg = re.findall(r'setTimeout\(\"(\S+)\((\d+)\)\"', html)[0]

        # 修改JS函数，使其返回Cookie内容
        js_func = js_func.replace('eval("qo=eval;qo(po);")', 'return po;')
        code = execjs.compile(js_func)

        # 执行JS获取Cookie
        cookie_str = code.call(js_arg[0], js_arg[1])
        cookie = re.findall(r"cookie='(\S+)", cookie_str)[0]
        if 'Set-Cookie' in resp.headers:
            cookie += re.findall(r'^\S+', resp.headers['Set-Cookie'])[0]
        # self.logger.info(cookie)
        self.headers['Cookie'] = cookie

    async def handle(self, resp):
        return re.findall(r'(\d+\.\d+\.\d+\.\d+)[\S\s]+?(\d+)</td><td>',
                          await resp.text())


if __name__ == '__main__':
    Fetcher.test()
