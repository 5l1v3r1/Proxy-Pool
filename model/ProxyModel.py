# coding:utf-8
import re
from _sha1 import sha1
from datetime import datetime
from enum import IntEnum

from sqlalchemy import Column, String, SmallInteger, Enum, Integer, DateTime

from connector.base_connector import BaseConnector
from utils import Config


class Anonymity(IntEnum):
    Transparent = 0  # 透明代理
    Anonymous = 1  # 普通匿名
    Confuse = 2  # 混淆
    Elite = 3  # 高度匿名

    def __str__(self):
        return self.name


class ProxyModel(Config.Base):
    __tablename__ = 'proxy'
    unique_id = Column(String(40), primary_key=True)
    ip = Column(String(15), nullable=False)
    port = Column(Integer, nullable=False)
    anonymity = Column(SmallInteger, default=1)
    protocol = Column(Enum('http', 'https', 'socks4', 'socks5', 'VPN'), default='http')
    speed = Column(Integer, default=0)
    ip_feedback = Column(String(255))
    extra_headers = Column(String(1024))
    usable = Column(SmallInteger, default=1)
    verifiable = Column(SmallInteger, default=1)
    auth = Column(SmallInteger, default=0)
    success = Column(Integer, default=1)
    failed = Column(Integer, default=0)
    verified_at = Column(DateTime, default=datetime.now)  # Last time that passed verify
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    exception = None
    connector = None

    @property
    def uid(self):
        _sha1 = sha1()
        _sha1.update(self.url.encode())
        return _sha1.hexdigest()

    @classmethod
    def from_url(cls, proxy: str):
        if not proxy:
            return None
        ret = re.findall(r'^(\w+)://(?:(\S*):(\S+)@)?(\S+?):(\d+)$', proxy)
        if not ret:
            return None
        return cls(*ret[0])

    def __init__(self, protocol='', username='', password='', ip='', port=0):
        self.protocol = protocol
        self.ip = ip
        self.port = int(port)
        self.auth = False
        self.username = username
        self.password = password
        if username.strip() or password.strip():
            self.auth = True
        self.unique_id = self.uid
        self.connector = None

    def init(self, conn=None):
        self.usable = False
        if conn and issubclass(conn, BaseConnector):
            self.connector = conn(self.protocol, self.ip, self.port)
        else:
            self.connector = None

    @property
    def url(self):
        return '%s://%s:%s' % (self.protocol, self.ip, self.port)

    def __str__(self):
        return self.url

    def __repr__(self):
        return '<usable=%s, url=%s, anonymity=%s, speed=%d>' % (
            self.usable, self.url, self.anonymity, self.speed
        )

    def log(self, msg, *args, **kwargs):
        Config.logger.debug('%s: %s' % (self.url, msg))

