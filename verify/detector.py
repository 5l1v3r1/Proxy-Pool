import asyncio
import json
import os
import socket
from urllib.parse import urlparse

from model import Anonymity
from model import ProxyModel
from utils.functions import get_self_ip

CRLF = "\r\n"
WHITESPACE = " "
FIELD_VALUE_SEP = ": "
HOST_PORT_SEP = ":"
SLASH = "/"
PROTO_HTTP = "http"
PROTO_HTTPS = "https"
HEADER_HOST = "Host"
HEADER_CONTENT_LENGTH = "Content-Length"


def _get_body_length(body):
    """
    Get len of string or file
    :param body:
    :return:
    :rtype: int
    """
    try:
        return len(body)
    except TypeError:
        try:
            return os.fstat(body.fileno()).st_size
        except (AttributeError, OSError):
            return None


class Detector:
    """Proxy Detector."""

    def __init__(self, url, ext_ip=None, timeout=5):
        self.url = url
        self.scheme = urlparse(url).scheme.upper()
        split = urlparse(url).netloc.split(':')
        self.host = split[0]
        self.ip = socket.gethostbyname(split[0])
        self._real_ext_ip = ext_ip or get_self_ip()
        if len(split) == 2:
            self.port = int(split[1])
        else:
            self.port = 80

        self.path = url.split(self.host)[-1]
        self.timeout = timeout

        self._default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.321.132 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive'
        }

    def build_request(self, method, body="", fullpath=False, headers=None):
        """
        :param method:
        :type method: basestring
        :param request_uri:
        :type request_uri: basestring
        :param body:
        :type body: basestring or file
        :param headers:
        :type headers: dict
        :return:
        :rtype: basestring
        """

        if headers is None:
            headers = {}

        header_fields = self._default_headers
        header_fields.update(headers)
        if HEADER_HOST not in header_fields:
            host_port = self.host
            if self.port not in (80, 443):
                host_port += ':' + str(self.port)
            header_fields['Host'] = host_port
        if body and HEADER_CONTENT_LENGTH not in header_fields:
            body_length = _get_body_length(body)
            if body_length:
                header_fields[HEADER_CONTENT_LENGTH] = body_length

        request_url = 'http://%s%s' % (self.host, self.path) if fullpath else self.path

        request = method + WHITESPACE + request_url + WHITESPACE + 'HTTP/1.1' + CRLF

        for field, value in header_fields.items():
            request += field + ':' + str(value) + CRLF
        request += CRLF
        return request, header_fields

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
        return '<Detector [%s] %s>' % (self.scheme, self.host)
