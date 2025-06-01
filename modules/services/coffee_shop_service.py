from modules.models.coffeeshop import CoffeeShop
from modules.repository.coffee_repository import CoffeeShopRepository


class CoffeeShopService:
    def __init__(self, repository=None):
        if repository is None:
            repository = CoffeeShopRepository()
        self.repository = repository

    def get_shops(self, page=1, per_page=10, query=None):
        offset = (page - 1) * per_page
        filter_query = {}
        if query:
            filter_query["data.name"] = {"$regex": query, "$options": "i"}
        return self.repository.find_many(filter_query, skip=offset, limit=per_page)

    def add_or_update_coffee_shop(self, coffee_shop):
        existing = self.repository.get_coffe_shop_by_id(coffee_shop.get('id'))
        if existing is None:
            return self.repository.add_coffee_shop(coffee_shop)
        else:
            return self.repository.update_coffee_shop(coffee_shop)

    def count_coffee_shops(self, query=None):
        filter_query = {}
        if query:
            filter_query["tags.name"] = {"$regex": query, "$options": "i"}
        return self.repository.find_many(filter_query).get("total", 0)

    def get_coffee_shop_by_id(self, coffe_shop_id):
        return self.repository.get_coffe_shop_by_id(coffe_shop_id)

