# coding:utf-8
import time

import requests
from requests.models import Response

from utils.functions import random_user_agent


class WebRequest(object):

    @classmethod
    def header(cls):
        """
        basic header
        :return:
        """
        return {
            'User-Agent': random_user_agent(),
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'close',
            'Cache-Control': 'no-cache'
        }

    @classmethod
    def get(cls, url, header=None, retry_time=2, timeout=10,
            retry_flag=list(), retry_interval=0, **kwargs):
        """
        get method
        :param url: target url
        :param header: headers
        :param retry_time: retry time when network error
        :param timeout: network timeout
        :param retry_flag: if retry_flag in content. do retry
        :param retry_interval: retry interval(second)
        :param kwargs:
        :return:
        """
        headers = cls.header()
        if header and isinstance(header, dict):
            headers.update(header)
        while True:
            try:
                html = requests.get(url, headers=headers, timeout=timeout, **kwargs)
                if any(f in html.content for f in retry_flag):
                    raise Exception
                return html
            except Exception as e:
                print(e)
                retry_time -= 1
                if retry_time <= 0:
                    # 多次请求失败
                    resp = Response()
                    resp.status_code = 200
                    return resp
                time.sleep(retry_interval)
