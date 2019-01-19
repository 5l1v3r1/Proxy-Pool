# coding:utf-8
import os
from time import time

from six import add_metaclass
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from utils.classes import Singleton, ConfigParse
from utils.logger import LogHandler

SECTION_GENERAL = 'GENERAL'
SECTION_DB = 'DB'
SECTION_HOST = 'HOST'

pj_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
cfg_dir = os.path.join(pj_dir, 'config.ini')
config_file = ConfigParse()
config_file.read(cfg_dir)
config_file = config_file
section_general = config_file[SECTION_GENERAL]
section_host = config_file[SECTION_HOST]
_base = declarative_base()
_engine = create_engine(section_general['conn'], echo=False)
_session = sessionmaker(bind=_engine)


@add_metaclass(Singleton)
class Config:
    proxy = section_general.get('proxy', None)
    host_ip = section_host['ip']
    host_port = int(section_host['port'])
    PROJECT_DIR = pj_dir
    CONFIG_DIR = cfg_dir
    start_time = int(time())
    RAW_PROXY = 'raw_proxy'
    USABLE_PROXY = 'usable_proxy'
    Base = _base
    engine = _engine
    Session = _session
    logger = LogHandler('Common')


__all__ = ['Config']

if __name__ == '__main__':
    print(Config.db_type)
    print(Config.db_name)
    print(Config.db_host)
    print(Config.db_port)
    print(Config.host_ip)
    print(Config.host_port)
    print(Config.__dict__)
