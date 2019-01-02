# -*- coding: utf-8 -*-
from utils import Config


def test_get_config():
    """
    test class Config in Util/Config
    :return:
    """
    gg = Config()
    print(gg.db_type)
    print(gg.db_name)
    print(gg.db_host)
    print(gg.db_port)
    assert isinstance(gg.proxy_getter_functions, list)
    print(gg.proxy_getter_functions)


if __name__ == '__main__':
    test_get_config()
