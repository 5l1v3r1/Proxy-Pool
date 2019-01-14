# coding:utf-8
import asyncio
import ipaddress
import os
import random
import socket

import aiodns
import aiohttp
import async_timeout
import requests

from utils import ipdb, Config
from utils.errors import ResolveError

ipdb_path = os.path.join(Config.PROJECT_DIR, 'utils', 'ipdb', 'mydata4vipday1.ipdb')


class Resolver:
    """Async host resolver based on aiodns."""

    _cached_hosts = {}
    _ip_hosts = [
        'https://wtfismyip.com/text',
        'http://api.ipify.org/',
        'http://ipinfo.io/ip',
        'http://ipv4.icanhazip.com/',
        'http://myexternalip.com/raw',
        'http://ipinfo.io/ip',
        'http://ifconfig.io/ip',
    ]

    def __init__(self, timeout=5, loop=None):
        self._timeout = timeout
        self._loop = loop or asyncio.get_event_loop()
        self._resolver = aiodns.DNSResolver(loop=self._loop)

    @staticmethod
    def host_is_ip(host):
        """Check a host is IP address."""
        # TODO: add IPv6 support
        try:
            ipaddress.IPv4Address(host)
        except ipaddress.AddressValueError:
            return False
        else:
            return True

    @staticmethod
    def get_ip_info(ip):
        """Return geo information about IP address.
        """
        if not Resolver.host_is_ip(ip):
            return None
        ret = requests.get('http://ipapi.ipip.net/find?addr=' + ip, timeout=5, headers={'Token': '800d61aa297ad456f66d0ca43848a7ede99d73fc'}).json()
        if ret['ret'] != 'ok':
            ip_loc = ipdb.City(ipdb_path)
            city = ip_loc.find_map(ip, 'CN')
        else:
            city = dict(zip([
                'country_name', 'region_name', 'city_name',
                'owner_domain', 'isp_domain', 'latitude',
                'longitude', 'timezone', 'utc_offset',
                'china_admin_code', 'idd_code', 'country_code',
                'continent_code'
            ], ret['data']))
        return city

    def _pop_random_ip_host(self):
        host = random.choice(self._ip_hosts)
        self._ip_hosts.remove(host)
        return host

    async def get_real_ext_ip(self):
        """Return real external IP address."""
        while self._ip_hosts:
            try:
                with async_timeout.timeout(self._timeout, loop=self._loop):
                    async with aiohttp.ClientSession(loop=self._loop) as session, session.get(self._pop_random_ip_host()) as resp:
                        ip = await resp.text()
            except asyncio.TimeoutError:
                pass
            else:
                ip = ip.strip()
                if self.host_is_ip(ip):
                    Config.logger.debug('Real external IP: %s', ip)
                    break
        else:
            raise RuntimeError('Could not get the external IP')
        return ip

    async def resolve(self, host, port=80, family=None,
                      qtype='A', logging=True):
        """Return resolving IP address(es) from host name."""
        if self.host_is_ip(host):
            return host

        _host = self._cached_hosts.get(host)
        if _host:
            return _host

        resp = await self._resolve(host, qtype)

        if resp:
            hosts = [{'hostname': host, 'host': r.host, 'port': port,
                      'family': family, 'proto': socket.IPPROTO_IP,
                      'flags': socket.AI_NUMERICHOST} for r in resp]
            if family:
                self._cached_hosts[host] = hosts
            else:
                self._cached_hosts[host] = hosts[0]['host']
            if logging:
                Config.logger.debug('%s: Host resolved: %s' % (
                    host, self._cached_hosts[host]))
        else:
            if logging:
                Config.logger.warning('%s: Could not resolve host' % host)
        return self._cached_hosts.get(host)

    async def _resolve(self, host, qtype):
        try:
            resp = await asyncio.wait_for(self._resolver.query(host, qtype),
                                          timeout=self._timeout)
        except (aiodns.error.DNSError, asyncio.TimeoutError):
            raise ResolveError
        else:
            return resp
