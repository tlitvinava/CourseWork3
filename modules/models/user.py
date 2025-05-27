# -*- coding: utf-8 -*-
import uuid

class User:
    def __init__(self, username, password):
        self.id = str(uuid.uuid4())
        self.username = username
        self.password = password  # Для теста: в реальном проекте используйте хэширование!
        self.friends = []
        self.favorite_coffee_shops = []

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "friends": self.friends,
            "favorite_coffee_shops": self.favorite_coffee_shops
        }
