import asyncio
import json
import socket
from urllib.parse import urlparse

from db.model import Anonymity
from db.model import ProxyModel


class Judge:
    """Proxy Judge."""

    def __init__(self, url, timeout=5, loop=None):
        self.url = url
        self.scheme = urlparse(url).scheme.upper()
        self.host = urlparse(url).netloc
        self.path = url.split(self.host)[-1]
        split = self.host.split(':')
        self.ip = socket.gethostbyname(split[0])
        if len(split) == 2:
            self.port = int(split[1])
        else:
            self.port = 80
        self.timeout = timeout
        self._loop = loop or asyncio.get_event_loop()
        self.event = asyncio.Event()

    def parse_response(self, proxy: ProxyModel, resp: str, hdrs):
        resp = json.loads(resp)
        proxy.usable = True
        proxy.ip_feedback = resp['origin']
        ret_header = resp['headers']
        extra_headers = {}
        for x in ret_header:
            if x.lower() in ['host']:
                continue
            if x in hdrs and ret_header[x] == hdrs[x]:
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

    def __repr__(self):
        return '<Judge [%s] %s>' % (self.scheme, self.host)
