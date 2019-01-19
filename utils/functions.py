# coding:utf-8
import json
import os
import random
import re
from urllib.request import urlopen, Request

from utils import Config, ipdb

IPPattern = re.compile(
    r'(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)')

IPPortPatternLine = re.compile(
    r'^.*?(?P<ip>(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)).*?(?P<port>\d{1,5}).*$',  # noqa
    flags=re.MULTILINE)

IPPortPatternGlobal = re.compile(
    r'(?P<ip>(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?))'  # noqa
    r'(?=.*?(?:(?:(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?))|(?P<port>\d{1,5})))',  # noqa
    flags=re.DOTALL)


def random_user_agent():
    """
    return an User-Agent at random
    :return:
    """
    ua_list = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
        'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
    ]
    return random.choice(ua_list)


def get_self_ip():
    return json.loads(urlopen('http://httpbin.skactor.tk:8080/ip').read().decode('utf-8'))['origin']


def ip_location(ip):
    if not IPPattern.match(ip):
        return None
    ret = json.loads(urlopen(Request('http://ipapi.ipip.net/find?addr=' + ip, headers={'Token': '800d61aa297ad456f66d0ca43848a7ede99d73fc'})).read().decode())
    if ret['ret'] != 'ok':
        ip_loc = ipdb.City(os.path.join(Config.PROJECT_DIR, 'utils', 'ipdb', 'mydata4vipday1.ipdb'))
        city = ip_loc.find_map(ip, 'CN')
    else:
        city = dict(zip([
            'country_name', 'region_name', 'city_name',
            'owner_domain', 'isp_domain', 'latitude',
            'longitude', 'timezone', 'utc_offset',
            'china_admin_code', 'idd_code', 'country_code',
            'continent_code'
        ], ret['data']))
        # city = CityInfo(**city)
    return city


if __name__ == '__main__':
    ip_location('127.0.0.1')
