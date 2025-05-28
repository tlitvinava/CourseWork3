# -*- coding: utf-8 -*-
from modules.models.coffeeshop import CoffeeShop
from modules.repository.coffee_repository import CoffeeShopRepository

class CoffeeShopService:
    def __init__(self, repository=None):
        if repository is None:
            repository = CoffeeShopRepository()
        self.repository = repository

    def create_coffee_shop(self, name, address, **attributes):
        shop = CoffeeShop(name, address, **attributes)
        return self.repository.add(shop)

    def list_coffee_shops(self):
        shops = self.repository.list_all()
        return [shop.to_dict() for shop in shops]

    # Дополнительно можно добавить методы для update, delete и get по id.
