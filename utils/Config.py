# -*- coding: utf-8 -*-
from six.moves import configparser
import os

from six import add_metaclass

from utils.util_classes import Singleton

SECTION_DB = 'DB'
SECTION_HOST = 'HOST'


@add_metaclass(Singleton)
class Config(object):
    """
    to get config from config.ini
    """

    def __init__(self):
        self.pwd = os.path.split(os.path.realpath(__file__))[0]
        self.config_path = os.path.join(os.path.split(self.pwd)[0], 'config.ini')
        config_file = configparser.ConfigParser()
        config_file.read(self.config_path)
        self.config_file = config_file
        section_db = config_file[SECTION_DB]
        section_host = config_file[SECTION_HOST]
        self.__dict__.update({
            'db_type': section_db['type'],
            'db_name': section_db['name'],
            'db_host': section_db['host'],
            'db_port': section_db['port'],
            'proxy_getter_functions': config_file['ProxyFetcher'],
            'host_ip': section_host['ip'],
            'host_port': int(section_host['port'])
        })


if __name__ == '__main__':
    gg = Config()
    print(gg.db_type)
    print(gg.db_name)
    print(gg.db_host)
    print(gg.db_port)
    print(gg.proxy_getter_functions)
    for i in gg.proxy_getter_functions:
        print(i)
    print(gg.host_ip)
    print(gg.host_port)
