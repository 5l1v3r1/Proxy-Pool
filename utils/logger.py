# coding:utf-8
import os
from logging import Logger, Formatter, StreamHandler
from logging.handlers import TimedRotatingFileHandler

from utils import Config

# 日志级别
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

LOG_PATH = os.path.join(Config.PROJECT_DIR, 'log')


class LogHandler(Logger):
    """
    LogHandler
    """

    def __init__(self, name, level=INFO, stream=True, file=True):
        super(LogHandler, self).__init__(name, level=level)
        if stream:
            self.__setStreamHandler()
        if file:
            self.__setFileHandler()

    def __setFileHandler(self, level=None):
        """
        set file handler
        :param level:
        :return:
        """
        file_name = os.path.join(LOG_PATH, '{name}.log'.format(name=self.name))
        # 设置日志回滚, 保存在log目录, 一天保存一个文件, 保留15天
        file_handler = TimedRotatingFileHandler(filename=file_name, when='D', interval=1, backupCount=15)
        file_handler.suffix = '%Y%m%d.log'
        if not level:
            file_handler.setLevel(self.level)
        else:
            file_handler.setLevel(level)
        formatter = Formatter('%(asctime)s %(name)s:[%(levelname)s] %(message)s')

        file_handler.setFormatter(formatter)
        self.file_handler = file_handler
        self.addHandler(file_handler)

    def __setStreamHandler(self, level=None):
        """
        set stream handler
        :param level:
        :return:
        """
        stream_handler = StreamHandler()
        formatter = Formatter('%(asctime)s %(name)s:[%(levelname)s] %(message)s')
        stream_handler.setFormatter(formatter)
        if not level:
            stream_handler.setLevel(self.level)
        else:
            stream_handler.setLevel(level)
        self.addHandler(stream_handler)

    def rename(self, name):
        """
        reset name
        :param name:
        :return:
        """
        self.name = name
        self.removeHandler(self.file_handler)
        self.__setFileHandler()


if __name__ == '__main__':
    log = LogHandler('test')
    log.info('this is a test msg')
