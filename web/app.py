# coding:utf-8
from datetime import datetime

import requests
from jinja2 import Environment, PackageLoader
from sanic import Sanic
from sanic.response import json, html

from manager.proxy_manager import ProxyManager
from utils import Config

env = Environment(loader=PackageLoader('web', 'templates'))

app = Sanic(__name__)

proxy_manager = ProxyManager()


@app.route('/')
async def index(request):
    template = env.get_template('index.html')
    html_content = template.render()
    return html(html_content)


@app.route('/api/web-request-speed')
async def web_request_speed(request):
    data = request.args
    try:
        proxy_url = data.get('proxy_url')
        web_link = data.get('web_link',
                            'http://httpbin.skactor.tk:8080/anything')
        resp = requests.get(web_link, proxies={
            'http': proxy_url, 'https': proxy_url}).text
    except Exception as e:
        return str(e)
    return html(resp)


@app.route('/api/proxy', methods=['GET', 'POST'])
async def api_proxy(request):
    args = request.json or {}
    start = int(args['start'] if 'start' in args else 0)
    length = int(args['length'] if 'length' in args else 10)
    draw = int(args['draw'] if 'draw' in args else 1)
    order = args['order'] if 'order' in args else []
    if order:
        column_name = args['columns'][order[0]['column']]['name']
        print('Order by', column_name)
        result_list = proxy_manager.all_usable_proxy_with_loc(start, length,
                                                              column_name,
                                                              order[0]['dir'])
    else:
        result_list = proxy_manager.all_usable_proxy_with_loc(start, length)

    total = proxy_manager.all_usable_proxy_count()
    ret = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': total,
           'data': []}
    i = start + 1
    for result in result_list:
        proxy = result[0]
        location = result[1]
        ret['data'].append({
            'id': i,
            'uid': proxy.unique_id,
            'ip': proxy.ip,
            'port': proxy.port,
            'speed': proxy.speed,
            'location': ' '.join([location.country_name, location.region_name,
                                  location.city_name]),
            'isp': location.isp_domain,
            'protocol': proxy.protocol,
            'anonymity': proxy.anonymity,
            'verified': datetime.strftime(proxy.verified_at,
                                          '%Y-%m-%d %H:%M:%S'),
            'ctrl':
                '<button class="btn btn-sm btn-copy mr-2" data-url="%s" data-unique-id="%s">复制</button>'
                '<button class="btn btn-sm btn-speed" data-url="%s" data-unique-id="%s">测速</button>'
                % (proxy.url, proxy.unique_id, proxy.url, proxy.unique_id)
        })
        i += 1
    return json(ret)


def run():
    app.run(host=Config.host_ip, port=Config.host_port)


if __name__ == '__main__':
    run()
