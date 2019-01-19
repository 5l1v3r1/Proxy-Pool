# coding:utf-8
import zlib


class BaseConnector:
    def __init__(self, protocol, ip, port, timeout=5):
        self.protocol = protocol
        self.ip = ip
        self.port = port
        self._closed = True
        self._timeout = timeout

    def connect(self):
        pass

    def close(self):
        pass

    def send(self, req):
        pass

    def recv(self, length=0, status_code=False):
        pass

    @staticmethod
    def decompress_content(headers, content):
        is_compressed = headers.get('Content-Encoding') in ('gzip', 'deflate')
        if is_compressed:
            # gzip: zlib.MAX_WBITS|16;
            # deflate: -zlib.MAX_WBITS;
            # auto: zlib.MAX_WBITS|32;
            try:
                content = zlib.decompress(content, zlib.MAX_WBITS | 32)
            except zlib.error:
                content = b''
        return content.decode('utf-8', 'ignore')
