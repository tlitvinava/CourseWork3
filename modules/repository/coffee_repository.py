# -*- coding: utf-8 -*-

class CoffeeShopRepository:
    def __init__(self):
        self.coffee_shops = {}  # Хранение кофеен в словаре: {id: CoffeeShop}

    def add(self, coffee_shop):
        self.coffee_shops[coffee_shop.id] = coffee_shop
        return coffee_shop

    def list_all(self):
        return list(self.coffee_shops.values())

    def get(self, shop_id):
        return self.coffee_shops.get(shop_id)

    def update(self, shop_id, update_data):
        shop = self.get(shop_id)
        if shop:
            for key, value in update_data.items():
                if key == "name":
                    shop.name = value
                elif key == "address":
                    shop.address = value
                elif key == "attributes":
                    shop.attributes = value
            return shop
        return None

    def delete(self, shop_id):
        return self.coffee_shops.pop(shop_id, None)
