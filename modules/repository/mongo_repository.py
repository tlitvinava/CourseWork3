# -*- coding: utf-8 -*-
from pymongo import MongoClient

class MongoRepository:
    def __init__(self, uri="mongodb://localhost:27017", db_name="my_database"):
        """
        Подключается к MongoDB по указанному URI и выбирает базу данных.
        Параметр db_name — имя базы, в которой будут храниться данные.
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]






