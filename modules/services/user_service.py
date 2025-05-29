# -*- coding: utf-8 -*-
from modules.models.user import User
from modules.repository.mongo_repository import MongoRepository

class UserService:
    def __init__(self, repository=None):
        # Если репозиторий не передан, используем MongoRepository по умолчанию
        if repository is None:
            repository = MongoRepository(uri="mongodb://localhost:27017", db_name="my_database")
        self.repository = repository

    def register_user(self, username, password, phone, email, region):
        if self.repository.get_user_by_username(username) is not None:
            raise ValueError("Пользователь с таким именем уже существует")
        new_user = User(username, password, phone, email, region)
        self.repository.add_user(new_user)
        return new_user

    def login_user(self, username, password):
        user = self.repository.get_user_by_username(username)
        if user and user.password == password:
            return user
        return None

    def add_favorite(self, user_id, coffee_shop):
        """
        Добавляет кофейню (в виде словаря) в избранное пользователя с указанным ID.
        """
        return self.repository.add_favorite(user_id, coffee_shop)

    def remove_favorite(self, user_id, coffee_shop):
        """
        Удаляет кофейню из избранного пользователя.
        """
        return self.repository.remove_favorite(user_id, coffee_shop)
