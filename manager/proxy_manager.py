# coding:utf-8
import datetime

from sqlalchemy import asc, desc

from db.model.IPLocation import IPLocation
from db.model.ProxyModel import ProxyModel
from utils import Config


class ProxyManager:
    def __init__(self):
        self.session = Config.Session()
        self.session.close_all()

    def get_proxy(self, proxy: ProxyModel) -> ProxyModel:
        return self.session.query(ProxyModel).get(proxy.unique_id)

    def get_iploc(self, ip) -> IPLocation:
        return self.session.query(IPLocation).get(ip)

    def all_proxy(self):
        return self.session.query(ProxyModel).all()

    def all_usable_proxy(self):
        return self.session.query(ProxyModel).filter(ProxyModel.usable == 1).all()

    def all_usable_proxy_count(self):
        return self.session.query(ProxyModel).filter(ProxyModel.usable == 1).count()

    def all_usable_proxy_with_loc(self, start=0, length=10, column_name='speed', sort_by='asc'):
        ret = self.session.query(ProxyModel, IPLocation).filter(ProxyModel.usable == 1).filter(IPLocation.ip == ProxyModel.ip)

        if column_name not in ['ip', 'port', 'anonymity', 'protocol', 'speed', 'verified_at', 'updated_at', 'isp_domain']:
            column_name = 'speed'
        if sort_by == 'asc':
            ret = ret.order_by(asc(column_name))
        else:
            ret = ret.order_by(desc(column_name))
        ret = ret.limit(length).offset(start)
        return ret.all()

    def proxy_verified_before(
            self, days: float = 0, seconds: float = 0, microseconds: float = 0,
            milliseconds: float = 0, minutes: float = 0, hours: float = 0, weeks: float = 0
    ):
        return self.session.query(ProxyModel).filter(ProxyModel.verified_at < datetime.datetime.now() - datetime.timedelta(days, seconds, microseconds, milliseconds, minutes, hours, weeks)).all()

    def proxy_verified_after(
            self, days: float = 0, seconds: float = 0, microseconds: float = 0,
            milliseconds: float = 0, minutes: float = 0, hours: float = 0, weeks: float = 0
    ):
        return self.session.query(ProxyModel).filter(ProxyModel.verified_at > datetime.datetime.now() - datetime.timedelta(days, seconds, microseconds, milliseconds, minutes, hours, weeks)).all()

    def add_iploc(self, ip):
        ip_loc = self.get_iploc(ip)
        if not ip_loc:
            self.session.add(IPLocation(ip))
        self.commit()

    def add_proxy(self, proxy: ProxyModel):
        ori_proxy = self.get_proxy(proxy)
        if ori_proxy:
            if proxy.usable:
                ori_proxy.speed = proxy.speed
                ori_proxy.success += 1
            else:
                ori_proxy.usable = 0
                ori_proxy.failed += 1
            ori_proxy.updated_at = datetime.datetime.now()
        else:
            if proxy.usable:
                self.add_iploc(proxy.ip)
                self.session.add(proxy)
        self.commit()

    def verify_passed(self, proxy: ProxyModel):
        proxy.success += 1

    def verify_failed(self, proxy: ProxyModel):
        proxy.failed += 1

    def commit(self):
        self.session.commit()

    def close(self):
        self.session.close()
