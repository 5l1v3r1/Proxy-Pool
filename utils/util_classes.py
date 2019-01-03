# -*- coding: utf-8 -*-
from abc import ABCMeta

from six.moves import configparser


class ConfigParse(configparser.ConfigParser):
    """
    rewrite ConfigParser, for support upper option
    """

    def __init__(self, *args, **kwargs):
        super(ConfigParse, self).__init__(*args, **kwargs)

    def optionxform(self, optionstr):
        return optionstr


class Singleton(ABCMeta):
    """
    Singleton Metaclass
    """

    _inst = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._inst:
            cls._inst[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._inst[cls]
