# coding:utf-8
import os
import random

import requests

from utils import Config, ipdb

ip_loc = None


def verify_proxy_format(proxy: str):
    """
    检查代理格式
    :param proxy:
    :return:
    """
    proxy_split = proxy.split(':')
    if len(proxy_split) != 2:
        return False
    return vaild_ip(proxy_split[0]) and proxy_split[1].isdigit() and 0 < int(proxy_split[1]) < 65536


def vaild_ip(ip: str):
    ip_split = ip.strip().split('.')
    if len(ip_split) != 4:
        return False
    for i in ip_split:
        if not i.isdigit() or int(i) > 255 or int(i) < 0:
            return False
    return True


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


def ip_location(ip):
    global ip_loc
    if not vaild_ip(ip):
        return None
    ret = requests.get('http://ipapi.ipip.net/find?addr=' + ip, timeout=5, headers={'Token': '800d61aa297ad456f66d0ca43848a7ede99d73fc'}).json()
    if ret['ret'] != 'ok':
        if not ip_loc:
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
