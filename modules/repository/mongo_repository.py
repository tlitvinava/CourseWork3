# -*- coding: utf-8 -*-
from pymongo import MongoClient
from modules.models.user import User

class MongoRepository:
    def __init__(self, uri="mongodb://localhost:27017", db_name="my_database"):
        """
        Подключается к MongoDB по указанному URI и выбирает базу данных.
        Параметр db_name — имя базы, в которой будут храниться данные.
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.users_collection = self.db["users"]

    def add_user(self, user):
        data = user.to_dict()
        self.users_collection.insert_one(data)
        return user

    def update_user(self, user):
        data = user.to_dict()
        # Обновляем документ по идентификатору пользователя, создавая его, если его нет (upsert)
        self.users_collection.replace_one({"id": user.id}, data, upsert=True)
        return user

    def get_user_by_username(self, username):
        data = self.users_collection.find_one({"username": username})
        if data:
            return User.from_dict(data)
        return None

    def get_user_by_id(self, user_id):
        data = self.users_collection.find_one({"id": user_id})
        if data:
            return User.from_dict(data)
        return None

    def add_favorite(self, user_id, coffee_shop):
        user = self.get_user_by_id(user_id)
        if user:
            if coffee_shop not in user.favorites:
                user.favorites.append(coffee_shop)
                self.update_user(user)
                return True  # Добавлено
            return False  # Уже есть
        return None  # Пользователь не найден

    def remove_favorite(self, user_id, coffee_shop):
        user = self.get_user_by_id(user_id)
        if user:
            if coffee_shop in user.favorites:
                user.favorites.remove(coffee_shop)
                self.update_user(user)
            return user
        return None
