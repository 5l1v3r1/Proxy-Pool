# coding:utf-8
import json
import pycurl
import time
from enum import IntEnum

import certifi
from requests import Timeout
from six import BytesIO

from utils import LogHandler, proxy_split, WebRequest, user_agent

logger = LogHandler('ProxyVerifier')


class Anonymity(IntEnum):
    Transparent = 0  # 透明代理
    Anonymous = 1  # 普通匿名
    Confuse = 2  # 混淆
    Elite = 3  # 高度匿名


class VerifyRet(object):
    protocol = None
    usable = False
    anonymity = Anonymity.Anonymous
    speed = 0
    ip_equal = True
    ip_origin = ''
    ip_feedback = ''
    extra_headers = {}


class ProxyVerifier:
    def header(self):
        return {
            'User-Agent': user_agent(),
            'Accept': '*/*',
            'Connection': 'close'
        }

    def verify_all(self, proxy, your_ip=None):
        if not your_ip:
            your_ip = WebRequest.get('http://httpbin.org/ip', timeout=5).json()['origin']
        logger.info('Your IP: ' + your_ip)
        header = self.header()
        result = []
        for i in ['http', 'https', 'socks5']:
            logger.debug('Verifying ' + i)
            ret = self.verify(your_ip, '%s://%s' % (i, proxy), header)
            if ret.usable:
                result.append(ret)
        return result

    def verify(self, your_ip, _proxy, header):
        result = VerifyRet()
        proxy = proxy_split(_proxy)
        result.protocol = proxy[0]
        if result.protocol == 'https':
            url = 'https://httpbin.org/anything'
        else:
            url = 'http://httpbin.org/anything'
        try:
            start = time.time() * 1000

            ret = json.loads(self.request(url, header, _proxy))
            result.speed = int(time.time() * 1000 - start)
            result.usable = True
        except Timeout:
            return result
        except Exception as e:
            logger.exception(e)
            return result
        result.ip_equal = ret['origin'] == proxy[1]
        result.ip_origin = proxy[1]
        result.ip_feedback = ret['origin']
        ret_header = ret['headers']
        if ret_header == header:
            result.anonymity = Anonymity.Elite
        else:
            for x in ret_header:
                if x.upper() in ['HOST']:
                    continue
                if x in header and ret_header[x] == header[x]:
                    continue
                result.extra_headers[x] = ret_header[x]
                if 'X-Forwarded-For'.upper() == x.upper():
                    if your_ip in ret_header[x]:
                        result.anonymity = Anonymity.Transparent
                    elif proxy[1] in ret_header[x]:
                        result.anonymity = Anonymity.Anonymous
                    else:
                        result.anonymity = Anonymity.Confuse
        return result

    @classmethod
    def request(self, url, header=None, _proxy=None):
        proxy = proxy_split(_proxy)
        if not proxy:
            logger.error('Bad Proxy: ' + _proxy)
            return None

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.WRITEDATA, buffer)

        if proxy:
            if proxy[0] == "socks4":
                c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)
            elif proxy[0] == "socks4a":
                c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4A)
            elif proxy[0] == "socks5":
                c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
            elif proxy[0] == "socks5h":
                c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
            else:
                c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)

            c.setopt(pycurl.PROXY, proxy[1])
            c.setopt(pycurl.PROXYPORT, int(proxy[2]))
        if header:
            c.setopt(pycurl.HTTPHEADER, [k + ': ' + v for k, v in header.items()])
        c.setopt(pycurl.CAINFO, certifi.where())
        c.perform()
        c.close()
        body = buffer.getvalue()
        buffer.close()
        return body.decode()


if __name__ == '__main__':
    print('/'.join([i.protocol for i in ProxyVerifier.verify_all('127.0.0.1:1080')]))
