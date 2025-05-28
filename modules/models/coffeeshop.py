# -*- coding: utf-8 -*-
import uuid

class CoffeeShop:
    def __init__(self, name, address, **attributes):
        self.id = str(uuid.uuid4())
        self.name = name
        self.address = address
        self.attributes = attributes  # Дополнительные параметры: цена, меню, наличие Wi-Fi и т.д.

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "attributes": self.attributes
        }
