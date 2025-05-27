# -*- coding: utf-8 -*-
from modules.models.user import User
from modules.repository.repository import InMemoryRepository

class UserService:
    def __init__(self, repository=None):
        if repository is None:
            repository = InMemoryRepository()
        self.repository = repository

    def register_user(self, username, password):
        # Проверяем, существует ли пользователь с таким именем
        if self.repository.get_user_by_username(username) is not None:
            raise ValueError("Пользователь с таким именем уже существует")
        new_user = User(username, password)
        self.repository.add_user(new_user)
        return new_user

    def get_user(self, user_id):
        return self.repository.get_user_by_id(user_id)
