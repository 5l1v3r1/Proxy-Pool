# coding: utf-8
from pymongo import MongoClient

from db.DBClient import DBClient
from db.IDBClient import IDBClient


class MongodbClient(IDBClient):
    def __init__(self, name, host, port):
        super(MongodbClient, self).__init__()
        self.name = name
        self.client = MongoClient(host, port)
        self.db = self.client.proxy

    def change_table(self, name):
        self.name = name

    def get(self, proxy, **kwargs):
        data = self.db[self.name].find_one({'proxy': proxy})
        return data['num'] if data is not None else None

    def put(self, proxy, num=1):
        if self.db[self.name].find_one({'proxy': proxy}):
            return None
        else:
            self.db[self.name].insert({'proxy': proxy, 'num': num})

    def pop(self):
        data = list(self.db[self.name].aggregate([{'$sample': {'size': 1}}]))
        if data:
            data = data[0]
            value = data['proxy']
            self.delete(value, )
            return {'proxy': value, 'value': data['num']}
        return None

    def delete(self, value, **kwargs):
        self.db[self.name].remove({'proxy': value})

    def get_all(self):
        return {p['proxy']: p['num'] for p in self.db[self.name].find()}

    def clean(self):
        self.client.drop_database('proxy')

    def delete_all(self):
        self.db[self.name].remove()

    def update(self, key, value, **kwargs):
        self.db[self.name].update({'proxy': key}, {'$inc': {'num': value}}, )

    def exists(self, key, **kwargs):
        return True if self.db[self.name].find_one({'proxy': key}) is not None else False

    def get_size(self):
        return self.db[self.name].count()


if __name__ == "__main__":
    db = MongodbClient('first', 'localhost', 27017)
    # db.put('127.0.0.1:1')
    # db2 = MongodbClient('second', 'localhost', 27017)
    # db2.put('127.0.0.1:2')
    print(db.pop())
