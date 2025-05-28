# -*- coding: utf-8 -*-
import uuid

class User:
    def __init__(self, username, password, phone, email, region):
        self.id = str(uuid.uuid4())
        self.username = username
        self.password = password  # В реальном проекте пароль необходимо хэшировать!
        self.phone = phone
        self.email = email
        self.region = region

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "phone": self.phone,
            "email": self.email,
            "region": self.region
        }
