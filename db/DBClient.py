# -*- coding: utf-8 -*-
import os
import sys

from db.IDBClient import IDBClient
from utils import Config

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class DBClient(IDBClient):
    """
    DBClient DB工厂类 提供get/put/pop/delete/get_all/change_table/get_size方法

    目前存放代理的table/collection/hash有两种：
        RAW_PROXY： 存放原始的代理；
        USABLE_PROXY： 存放检验后的代理；

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
            SSDB：SSDBClient.py
            REDIS:RedisClient.py

    """

    def __init__(self):
        """
        init
        :return:
        """
        self.__init_db()

    def __init_db(self):
        """
        init DB Client
        :return:
        """
        __type = None
        if "SSDB" == Config.db_type:
            __type = "SSDBClient"
        elif "REDIS" == Config.db_type:
            __type = "RedisClient"
        elif "MONGODB" == Config.db_type:
            __type = "MongodbClient"
        else:
            pass
        assert __type, 'type error, Not support DB type: {}'.format(Config.db_type)
        self.client = getattr(__import__(__type), __type)(name=Config.db_name, host=Config.db_host, port=Config.db_port)

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
