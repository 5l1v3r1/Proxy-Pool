# coding:utf-8
import json
import os
import random
import re
from urllib.request import urlopen, Request

from utils import Config, ipdb
from utils.errors import BadStatusLine

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


def get_headers():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.321.132 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Pragma': 'no-cache',
        'Cache-control': 'no-cache',
        'Referer': 'https://www.google.com/'}
    return headers


def get_self_ip():
    return json.loads(urlopen('http://httpbin.skactor.tk:8080/ip').read().decode('utf-8'))['origin']


def get_all_ip(page):
    # TODO: add IPv6 support
    return set(IPPattern.findall(page))


def get_status_code(resp, start=9, stop=12):
    try:
        code = int(resp[start:stop])
    except ValueError:
        return 400  # Bad Request
    else:
        return code


def parse_status_line(line):
    _headers = {}
    is_response = line.startswith('HTTP/')
    try:
        if is_response:  # HTTP/1.1 200 OK
            version, status, *reason = line.split()
        else:  # GET / HTTP/1.1
            method, path, version = line.split()
    except ValueError:
        raise BadStatusLine(line)

    _headers['Version'] = version.upper()
    if is_response:
        _headers['Status'] = int(status)
        reason = ' '.join(reason)
        reason = reason.upper() if reason.lower() == 'ok' else reason.title()
        _headers['Reason'] = reason
    else:
        _headers['Method'] = method.upper()
        _headers['Path'] = path
        if _headers['Method'] == 'CONNECT':
            host, port = path.split(':')
            _headers['Host'], _headers['Port'] = host, int(port)
    return _headers


def parse_headers(headers):
    headers = headers.decode('utf-8', 'ignore').split('\r\n')
    _headers = {}
    _headers.update(parse_status_line(headers.pop(0)))

    for h in headers:
        if not h:
            break
        name, val = h.split(':', 1)
        _headers[name.strip().title()] = val.strip()

    if ':' in _headers.get('Host', ''):
        host, port = _headers['Host'].split(':')
        _headers['Host'], _headers['Port'] = host, int(port)
    return _headers


def ip_location(ip):
    if not IPPattern.match(ip):
        return None
    ret = json.loads(urlopen(Request('http://ipapi.ipip.net/find?addr=' + ip, headers={'Token': '800d61aa297ad456f66d0ca43848a7ede99d73fc'})).read().decode())
    print(ret)
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
