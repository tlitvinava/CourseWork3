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
