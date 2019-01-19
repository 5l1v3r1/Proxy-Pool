# coding:utf-8
import sys
from datetime import datetime

from flask import Flask, render_template, json, request

sys.path.append('../')

from utils import Config
from manager import ProxyManager

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
proxy_manager = ProxyManager()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/proxy', methods=['POST'])
def api_proxy():
    args = request.json or {}
    start = int(args['start'] if 'start' in args else 0)
    length = int(args['length'] if 'length' in args else 10)
    draw = int(args['draw'] if 'draw' in args else 1)
    order = args['order'] if 'order' in args else []
    if order:
        column_name = args['columns'][order[0]['column']]['name']
        print('Order by', column_name)
        result_list = proxy_manager.all_usable_proxy_with_loc(start, length, column_name, order[0]['dir'])
    else:
        result_list = proxy_manager.all_usable_proxy_with_loc(start, length)

    total = proxy_manager.all_usable_proxy_count()
    ret = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': total, 'data': []}
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
            'location': ' '.join([location.country_name, location.region_name, location.city_name]),
            'isp': location.isp_domain,
            'protocol': proxy.protocol,
            'anonymity': proxy.anonymity,
            'verified': datetime.strftime(proxy.verified_at, '%Y-%m-%d %H:%M:%S'),
            'ctrl': '<button class="btn btn-sm btn-copy mr-2" data-url="%s" data-unique-id="%s">复制</button><button class="btn btn-sm btn-speed" data-unique-id="%s">测速</button>'
                    % (proxy.url, proxy.unique_id, proxy.unique_id)
        })
        i += 1
    return json.jsonify(ret)


def run():
    app.run(host=Config.host_ip, port=Config.host_port)


if __name__ == '__main__':
    run()
