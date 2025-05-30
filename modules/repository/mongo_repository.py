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
        result = self.users_collection.replace_one({"id": user.id}, data, upsert=True)
        print(f"Modified count: {result.modified_count}")
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

    def get_favorites(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            return user.favorites
        return []

    def update_tags(self, user_id, coffee_shop, new_tag):
        coffee_id = coffee_shop.get('id')
        coffee_type = coffee_shop.get('type')

        try:
            coffee_id = int(coffee_id)
        except ValueError:
            pass

        if not coffee_id or not coffee_type:
            return None

        user = self.get_user_by_id(user_id)
        if not user:
            return None

        # Найти нужную кофейню и получить существующие теги
        existing_tags = []
        for fav in user.favorites:
            if fav.get('id') == coffee_id:
                existing_tags = fav.get('user_tags', [])
                break

        # Добавить тег, если его нет
        if new_tag not in existing_tags:
            existing_tags.append(new_tag)

        # Обновляем только user_tags для этой кофейни
        result = self.users_collection.update_one(
            {
                "id": user_id,
                "favorites.id": coffee_id,
            },
            {
                "$set": {
                    "favorites.$.user_tags": existing_tags
                }
            }
        )

        if result.modified_count == 0:
            print("Не удалось обновить теги")
            return None

        print("Теги успешно обновлены:", existing_tags)
        return self.get_user_by_id(user_id)


    def update_user_friends(self, user_id, friends_list):
        result = self.users_collection.update_one(
            {"id": user_id},
            {"$set": {"friends": friends_list}}
        )
        return result.modified_count > 0







