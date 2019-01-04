# coding:utf-8
from abc import ABC, abstractmethod


class IFetcher(ABC):
    name = None
    source = None
    enabled = True

    @abstractmethod
    def fetch(self):
        pass


__all__ = ['IFetcher']
