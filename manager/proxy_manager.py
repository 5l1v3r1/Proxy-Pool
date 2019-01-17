# coding:utf-8
import datetime

from sqlalchemy import asc, desc, update

from model import IPLocation
from model import ProxyModel
from utils import Config, LogHandler

logger = LogHandler('ProxyManager')


class ProxyManager:
    def __init__(self):
        self.session = Config.Session()

    def get_proxy(self, proxy: ProxyModel) -> ProxyModel:
        return self.session.query(ProxyModel).get(proxy.unique_id)

    def get_iploc(self, ip) -> IPLocation:
        return self.session.query(IPLocation).get(ip)

    def all_proxy(self):
        return self.session.query(ProxyModel).all()

    def all_iploc(self):
        return self.session.query(IPLocation).all()

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
            milliseconds: float = 0, minutes: float = 0, hours: float = 0, weeks: float = 0,
            limit=0
    ):
        ret = self.session.query(ProxyModel) \
            .filter(ProxyModel.verifiable == 1) \
            .filter(ProxyModel.verified_at < datetime.datetime.now() - datetime.timedelta(days, seconds, microseconds, milliseconds, minutes, hours, weeks))
        if limit:
            ret = ret.limit(limit)
        return ret.all()

    def proxy_verified_after(
            self, days: float = 0, seconds: float = 0, microseconds: float = 0,
            milliseconds: float = 0, minutes: float = 0, hours: float = 0, weeks: float = 0
    ):
        return self.session.query(ProxyModel) \
            .filter(ProxyModel.verifiable == 1) \
            .filter(ProxyModel.verified_at > datetime.datetime.now() - datetime.timedelta(days, seconds, microseconds, milliseconds, minutes, hours, weeks)) \
            .all()

    def add_iploc(self, ip):
        ip_loc = self.get_iploc(ip)
        if not ip_loc:
            self.session.add(IPLocation(ip))
        self.commit()

    def add_iploc_no_check(self, ip):
        self.session.add(IPLocation(ip))

    def add_proxy_no_check(self, proxy: ProxyModel):
        if proxy.usable:
            self.add_iploc(proxy.ip)
            self.session.add(proxy)

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
        if proxy.success - proxy.failed > 15:
            proxy.verifiable = 0

    def remove_bad_proxy(self):
        stmt = update(ProxyModel) \
            .where(ProxyModel.failed - ProxyModel.success > 15) \
            .where(ProxyModel.usable == 0) \
            .where(ProxyModel.verifiable == 1) \
            .values(verifiable=0)
        result = self.session.execute(stmt)
        logger.info('Removed %d useless proxies', result.rowcount)

    def commit(self):
        self.session.commit()

    def close(self):
        self.session.close()


if __name__ == '__main__':
    pm = ProxyManager()
    pm.remove_bad_proxy()
