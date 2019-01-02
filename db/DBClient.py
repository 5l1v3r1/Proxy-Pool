# -*- coding: utf-8 -*-
import os
import sys

from db.IDBClient import IDBClient
from utils import Config
from utils import Singleton

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class DBClient(IDBClient):
    """
    DbClient DB工厂类 提供get/put/pop/delete/getAll/changeTable方法

    目前存放代理的table/collection/hash有两种：
        raw_proxy： 存放原始的代理；
        useful_proxy_queue： 存放检验后的代理；

    抽象方法定义：
        get(proxy): 返回proxy的信息；
        put(proxy): 存入一个代理；
        pop(): 弹出一个代理
        exists(proxy)： 判断代理是否存在
        getNumber(raw_proxy): 返回代理总数（一个计数器）；
        update(proxy, num): 修改代理属性计数器的值;
        delete(proxy): 删除指定代理；
        getAll(): 返回所有代理；
        changeTable(name): 切换 table or collection or hash;


        所有方法需要相应类去具体实现：
            SSDB：SsdbClient.py
            REDIS:RedisClient.py

    """

    def __init__(self):
        """
        init
        :return:
        """
        self.config = Config()
        self.__init_db()

    def __init_db(self):
        """
        init DB Client
        :return:
        """
        __type = None
        if "SSDB" == self.config.db_type:
            __type = "SSDBClient"
        elif "REDIS" == self.config.db_type:
            __type = "RedisClient"
        elif "MONGODB" == self.config.db_type:
            __type = "MongodbClient"
        else:
            pass
        assert __type, 'type error, Not support DB type: {}'.format(self.config.db_type)
        self.client = getattr(__import__(__type), __type)(name=self.config.db_name, host=self.config.db_host, port=self.config.db_port)

    def get(self, key, **kwargs):
        return self.client.get(key, **kwargs)

    def put(self, key, **kwargs):
        return self.client.put(key, **kwargs)

    def update(self, key, value, **kwargs):
        return self.client.update(key, value, )

    def delete(self, key, **kwargs):
        return self.client.delete(key, )

    def exists(self, key, **kwargs):
        return self.client.exists(key, )

    def pop(self, **kwargs):
        return self.client.pop(**kwargs)

    def get_all(self):
        return self.client.get_all()

    def change_table(self, name):
        self.client.change_table(name)

    def get_size(self):
        return self.client.get_size()


if __name__ == "__main__":
    print(DBClient())
    print(DBClient())
