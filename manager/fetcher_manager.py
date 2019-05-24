# coding:utf-8
import inspect
import traceback
from collections import defaultdict

import six

from fetcher import BaseFetcher
from utils import Logger
from utils.misc import walk_modules

logger = Logger('FetcherManager')


def iter_module_classes(module, base_class):
    for obj in six.itervalues(vars(module)):
        if inspect.isclass(obj) and \
                obj is not base_class and \
                issubclass(obj, base_class) and \
                obj.__module__ == module.__name__ and \
                getattr(obj, 'name', None):
            yield obj


class BaseManager(object):
    _base_class = None

    def __init__(self):
        self._found = defaultdict(list)
        self._classes = {}

    def _check_name_duplicates(self):
        dupes = ["\n".join("  {cls} named {name!r} (in {module})".format(
            module=mod, cls=cls, name=name)
                           for (mod, cls) in locations)
                 for name, locations in self._found.items()
                 if len(locations) > 1]
        if dupes:
            msg = "There are several commands with the same name:\n\n{}\n\n" \
                  "  This can cause unexpected behavior.".format(
                "\n\n".join(dupes))
            logger.warn(msg)

    def load_path(self, path=None):
        try:
            for module in walk_modules(path):
                self.load(module)
        except ImportError as e:
            msg = "\n{tb}Could not load spiders from module '{modname}'. " \
                  "See above traceback for details.".format(
                modname=path, tb=traceback.format_exc())
            logger.warn(msg)

        self._check_name_duplicates()
        logger.debug('Loaded [%d] Commands' % len(self._classes))

    def load(self, module):
        for cls in iter_module_classes(module, self._base_class):
            self._found[cls.name].append(
                (module.__name__, cls.__name__))
            self._classes[cls.name] = cls

    def has_class(self, cls_name):
        return cls_name in self._classes

    def list(self):
        return self._classes

    def __getitem__(self, item):
        return self._classes.get(item.lower())


class FetcherManager(BaseManager):
    _base_class = BaseFetcher

    def __init__(self):
        super(FetcherManager, self).__init__()
        self.load_path('fetcher')
        self._cached = {}


if __name__ == '__main__':
    print(FetcherManager().list())
    # from manager import CheckProxy
    # CheckProxy.checkAllGetProxyFunc()
