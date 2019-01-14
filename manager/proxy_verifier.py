# coding:utf-8
import asyncio
import datetime
import time
from json import JSONDecodeError

import requests.adapters
import urllib3
from requests.exceptions import ChunkedEncodingError

from db.model import ProxyModel, Anonymity
from utils import LogHandler, random_user_agent

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = LogHandler('ProxyVerifier')


class ProxyVerifier:
    header = None
    ip = None

    def __init__(self, loop=None, self_ip=None):
        self.loop = loop or asyncio.get_event_loop()
        self.header = {
            'User-Agent': random_user_agent(),
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close'
        }
        if not self_ip:
            self_ip = requests.get('http://httpbin.skactor.tk:8080/ip', timeout=5).json()['origin']
            logger.info('Your IP: ' + self_ip)
        self.ip = self_ip

    def gen_tasks(self, proxy_url):
        tasks = []
        if '://' in proxy_url:
            urls = [proxy_url]
        else:
            urls = ['%s://%s' % (i, proxy_url) for i in ['http', 'https', 'socks5']]
        for url in urls:
            logger.debug('Verifying ' + url)
            proxy = ProxyModel.instance(url)
            if not proxy:
                logger.error(url)
                continue
            task = asyncio.ensure_future(self.verify(proxy), loop=self.loop)
            tasks.append(task)
        return tasks

    async def verify(self, proxy: ProxyModel):
        response = None
        try:
            proxy.verified_at = datetime.datetime.now()
            response = await self.loop.run_in_executor(None, self.__request, proxy)
            ret = response.json()
        except (
                requests.Timeout, urllib3.exceptions.TimeoutError, requests.exceptions.ProxyError,
                requests.exceptions.ConnectionError, ConnectionResetError, ChunkedEncodingError
        ) as e:
            proxy.exception = e
            return proxy
        except JSONDecodeError:
            logger.error('Json decode error when using %s' % proxy)
            logger.debug(response.text)
            return proxy
        except TypeError as e:
            if str(e) == "object of type 'NoneType' has no len()":
                proxy.auth = True
            return proxy
        except Exception as e:
            proxy.exception = e
            logger.error('Error with proxy: %s, exception type: %s' % (proxy, type(e)))
            logger.exception(e)
            return proxy
        self.__parse_response(proxy, ret)
        return proxy

    def __parse_response(self, proxy, resp):
        proxy.usable = True
        proxy.ip_feedback = resp['origin']
        ret_header = resp['headers']
        extra_headers = {}
        for x in ret_header:
            if x.lower() in ['host']:
                continue
            if x in self.header and ret_header[x] == self.header[x]:
                continue
            extra_headers[x] = ret_header[x]
        if len(extra_headers) == 0:
            proxy.anonymity = int(Anonymity.Elite)
        else:
            proxy.extra_headers = str(extra_headers)
            __forwarded = 'X-Forwarded-For'
            if __forwarded in extra_headers:
                if self.ip in ret_header[__forwarded]:
                    proxy.anonymity = int(Anonymity.Transparent)
                elif proxy.ip in ret_header[__forwarded]:
                    proxy.anonymity = int(Anonymity.Anonymous)
                else:
                    proxy.anonymity = int(Anonymity.Confuse)

    def __request(self, proxy: ProxyModel):
        if proxy.protocol.startswith('https'):
            url = 'https://httpbin.skactor.tk/anything'
        else:
            url = 'http://httpbin.skactor.tk:8080/anything'
        proxies = {'http': str(proxy), 'https': str(proxy)}
        start = time.time() * 1000
        ret = requests.get(url, headers=self.header, timeout=5, proxies=proxies, verify=False)
        proxy.speed = int(time.time() * 1000 - start)
        return ret
