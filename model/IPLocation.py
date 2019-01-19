# coding:utf-8
from datetime import datetime

from sqlalchemy import Column, String, DateTime

from utils import Config
from utils.functions import ip_location


class IPLocation(Config.Base):
    __tablename__ = 'ip_loc'
    ip = Column(String(18), primary_key=True)
    country_name = Column(String(36))
    region_name = Column(String(36))
    city_name = Column(String(36))
    owner_domain = Column(String(255))
    isp_domain = Column(String(255))
    latitude = Column(String(10))
    longitude = Column(String(10))
    timezone = Column(String(255))
    utc_offset = Column(String(36))
    china_admin_code = Column(String(10))
    idd_code = Column(String(10))
    country_code = Column(String(10))
    continent_code = Column(String(10))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, ip):
        data = ip_location(ip)
        self.ip = ip
        if data:
            for key in data:
                self.__dict__[key] = data[key]
