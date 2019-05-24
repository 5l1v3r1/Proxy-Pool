# coding:utf-8
from utils import Logger


def test_log_handler():
    """
    test function LogHandler  in Util/LogHandler
    :return:
    """
    log = Logger('test')
    log.info('this is a log from test')

    log.rename(name='test1')
    log.info('this is a log from test1')

    log.rename(name='test2')
    log.info('this is a log from test2')


if __name__ == '__main__':
    test_log_handler()
