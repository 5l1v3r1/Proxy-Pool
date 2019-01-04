# -*- coding: utf-8 -*-
import os
from time import time

from utils.util_classes import Singleton, ConfigParse

SECTION_GENERAL = 'GENERAL'
SECTION_DB = 'DB'
SECTION_HOST = 'HOST'

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CONFIG_DIR = os.path.join(PROJECT_DIR, 'config.ini')

Config = None

if not Config:
    config_file = ConfigParse()
    config_file.read(CONFIG_DIR)
    config_file = config_file
    section_general = config_file[SECTION_GENERAL]
    section_db = config_file[SECTION_DB]
    section_host = config_file[SECTION_HOST]

    Config = Singleton(
        'Config', (), {
            'proxy': section_general['proxy'],
            'db_type': section_db['type'],
            'db_name': section_db['name'],
            'db_host': section_db['host'],
            'db_port': section_db['port'],
            'host_ip': section_host['ip'],
            'host_port': int(section_host['port']),
            'project_dir': PROJECT_DIR,
            'config_dir': CONFIG_DIR,
            'start_time': int(time()),
            'RAW_PROXY': 'raw_proxy',
            'USABLE_PROXY': 'usable_proxy'
        }
    )

if __name__ == '__main__':
    print(Config.db_type)
    print(Config.db_name)
    print(Config.db_host)
    print(Config.db_port)
    print(Config.proxy_getter_functions)
    for i in Config.proxy_getter_functions:
        print(i)
    print(Config.host_ip)
    print(Config.host_port)
    print(Config.__dict__)
