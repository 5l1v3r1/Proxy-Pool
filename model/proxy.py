# coding:utf-8
from _sha1 import sha1
from datetime import datetime
from enum import IntEnum
from uuid import uuid4

from sqlalchemy import Column, String, SmallInteger, Enum, Integer, DateTime
from yarl import URL

from utils import Config


def uid():
    return uuid4().hex


class Anonymity(IntEnum):
    Transparent = 0  # 透明代理
    Anonymous = 1  # 普通匿名
    Confuse = 2  # 混淆
    Elite = 3  # 高度匿名

    def __str__(self):
        return self.name


class ProxyModel(Config.Base):
    __tablename__ = 'proxy'
    unique_id = Column(String(40), primary_key=True, default=uid)
    ip = Column(String(15), nullable=False)
    port = Column(Integer, nullable=False)
    anonymity = Column(SmallInteger, default=1)
    protocol = Column(Enum('http', 'https', 'socks4', 'socks5', 'VPN'),
                      default='http')
    speed = Column(Integer, default=0)
    ip_feedback = Column(String(255))
    extra_headers = Column(String(1024))
    usable = Column(SmallInteger, default=0)
    verifiable = Column(SmallInteger, default=1)
    auth = Column(SmallInteger, default=0)
    success = Column(Integer, default=1)
    failed = Column(Integer, default=0)
    verified_at = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def uid(self):
        _sha1 = sha1()
        _sha1.update(self.url.encode())
        return _sha1.hexdigest()

    @classmethod
    def from_url(cls, proxy_url: str):
        if not proxy_url:
            return None
        ret = URL(proxy_url)
        return cls(ret.scheme, ret.user, ret.password, ret.host, ret.port)

    def __init__(self, proto, username='', password='', ip='', port=80):
        self.protocol = proto
        self.ip = ip
        self.port = int(port) if port else 80
        self.auth = False
        self.usable = False
        self.username = username or ''
        self.password = password or ''
        if self.username.strip() or self.password.strip():
            self.auth = True
        self.unique_id = self.uid

    @property
    def url(self):
        return '%s://%s:%s' % (self.protocol, self.ip, self.port)

    def __str__(self):
        return self.url

    def __repr__(self):
        return '<usable=%s, url=%s, anonymity=%s, speed=%d>' % (
            self.usable, self.url, self.anonymity, self.speed
        )


if __name__ == '__main__':
    print(uid())
