# -*- coding: utf-8 -*-
from abc import abstractmethod

from six import add_metaclass

from utils import Singleton


@add_metaclass(Singleton)
class IDBClient:
    @abstractmethod
    def get(self, key, **kwargs):
        pass

    @abstractmethod
    def put(self, key, **kwargs):
        pass

    @abstractmethod
    def update(self, key, value, **kwargs):
        pass

    @abstractmethod
    def delete(self, key, **kwargs):
        pass

    @abstractmethod
    def exists(self, key, **kwargs):
        pass

    @abstractmethod
    def pop(self, **kwargs):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def change_table(self, name):
        pass

    @abstractmethod
    def get_size(self):
        pass
