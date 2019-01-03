# -*- coding: utf-8 -*-
from utils import Config


def test_get_config():
    """
    test class Config in Util/Config
    :return:
    """
    print(Config.db_type)
    print(Config.db_name)
    print(Config.db_host)
    print(Config.db_port)
    assert isinstance(Config.proxy_getter_functions, list)
    print(Config.proxy_getter_functions)


if __name__ == '__main__':
    test_get_config()
