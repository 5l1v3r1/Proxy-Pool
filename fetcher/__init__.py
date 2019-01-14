# coding:utf-8
from abc import ABC, abstractmethod


class IFetcher(ABC):
    name = None
    source = None
    enabled = True
    async = True

    @abstractmethod
    def fetch(self):
        pass

    def __str__(self):
        return '<name=%s, source=%s, enabled=%s, async=%s>' % (self.name, self.source, self.enabled, self.async)


__all__ = ['IFetcher']
