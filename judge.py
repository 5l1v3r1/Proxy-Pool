import json
import socket

from yarl import URL

from model import Anonymity
from model import ProxyModel
from utils.functions import get_self_ip


class Judge:
    """Proxy Judge."""

    def __init__(self, url):
        url = URL(url)
        self.url = url
        self.host = url.host
        self.ip = socket.gethostbyname(url.host)
        self.port = url.port
        self._real_ext_ip = get_self_ip()
        self._default_judge_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.321.132 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Pragma': 'no-cache',
            'Cache-control': 'no-cache',
            'Referer': 'https://www.google.com/'
        }

    def gen_request(self, method, fullpath=False, data=''):
        hdrs = self._default_judge_headers
        hdrs['Host'] = '%s:%s' % (self.host, self.port)
        hdrs['Connection'] = 'close'
        if method == 'POST':
            hdrs['Content-Length'] = str(len(data))
            hdrs['Content-Type'] = 'application/octet-stream'
        else:
            data = ''
        return '{method} {path} HTTP/1.1\r\n{headers}\r\n\r\n{data}'.format(
            method=method,
            path=self.url if fullpath else self.url.path_qs,
            headers='\r\n'.join([k + ': ' + v for k, v in hdrs.items()]),
            data=data
        ).encode(), hdrs

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
                if self._real_ext_ip in ret_header[__forwarded]:
                    proxy.anonymity = int(Anonymity.Transparent)
                elif proxy.ip in ret_header[__forwarded]:
                    proxy.anonymity = int(Anonymity.Anonymous)
                else:
                    proxy.anonymity = int(Anonymity.Confuse)

    def __repr__(self):
        return '<Judge [%s] %s>' % (self.url.scheme, self.url.host)
