# coding:utf-8
import datetime
import time
from _ssl import SSLError
from json import JSONDecodeError

import gevent
from gevent import socket
from utils._parser import HTTPParseError

from verify.connector import GeventConnector
from model import ProxyModel
from utils import LogHandler
from utils.errors import BadStatusError, RecvTimeout, ConnectTimeout, BadResponseError, ProxySendError
from utils.functions import get_self_ip
from verify.detector import Detector

logger = LogHandler('ProxyGeventVerifier')


class ProxyGeventVerifier:
    def __init__(self, post=False, timeout=4):
        ext_ip = get_self_ip()
        self._method = 'POST' if post else 'GET'
        self.http_judge = Detector('http://httpbin.skactor.tk:8080/anything', ext_ip)
        self.https_judge = Detector('https://httpbin.skactor.tk/anything', ext_ip)
        self._timeout = timeout

    def generate_tasks(self, proxies):
        tasks = []
        for proxy in proxies:
            proxy.init(GeventConnector)
            task = gevent.spawn(self.check, proxy)
            tasks.append(task)
        return tasks

    def check(self, proxy: ProxyModel):
        if proxy.protocol == 'https':
            judge = self.https_judge
        else:
            judge = self.http_judge
        content = None
        connector = proxy.connector
        try:
            start = time.time()
            connector.connect()  # connect to proxy
            proxy.speed = int((time.time() - start) * 1000)
            connector.negotiate(judge)  # proxy connect to test web
            request, request_headers = judge.build_request(self._method, fullpath=connector.use_full_path)  # build test request
            connector.send(request)  # send request
            content = connector.recv()  # fetch response
            judge.parse_response(proxy, content, request_headers)  # parse response body and verify anonymity of proxy
        except (socket.gaierror, RecvTimeout, ConnectTimeout, ConnectionResetError, IndexError, SSLError, ValueError, HTTPParseError, ConnectionAbortedError, BadResponseError, ProxySendError) as e:
            proxy.exception = e
        except BadStatusError as e:
            proxy.exception = e
        except JSONDecodeError:
            logger.error('Json decode error when using %s' % proxy)
            logger.debug(content)
        except Exception as e:
            proxy.exception = e
            logger.error('Unexpected exception: %s, exception type: %s' % (proxy, type(e)))
            logger.exception(e)
        proxy.verified_at = datetime.datetime.now()
        logger.debug('%s verified' % proxy)
        return proxy
