# -*- coding: utf-8 -*-
import uuid

class User:
    def __init__(self, username, password, phone, email, region, favorites=None, friends = None, id=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.username = username
        self.password = password
        self.phone = phone
        self.email = email
        self.region = region
        self.favorites = favorites if favorites is not None else []
        self.friends = friends if friends is not None else []

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "phone": self.phone,
            "email": self.email,
            "region": self.region,
            "favorites": self.favorites,
            "friends": self.friends,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            username=d.get("username"),
            password=d.get("password"),
            phone=d.get("phone"),
            email=d.get("email"),
            region=d.get("region"),
            favorites=d.get("favorites", []),
            id=d.get("id"),
            friends=d.get("friends", []),
        )
