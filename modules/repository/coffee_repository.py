from modules.models.coffeeshop import CoffeeShop
from modules.repository.mongo_repository import MongoRepository
from TSerializerPack.serializer import UniversalSerializer

class CoffeeShopRepository(MongoRepository):
    def __init__(self, uri="mongodb://localhost:27017", db_name="my_database"):
        super().__init__(uri, db_name)
        self.collection = self.db["coffeehouses"]
        self.serializer = UniversalSerializer(CoffeeShop)

    def add_coffee_shop(self, coffe_shop):
        data = self.serializer._to_dict(coffe_shop)
        self.collection.insert_one(data)
        return coffe_shop

    def update_coffee_shop(self, coffe_shop):
        data = self.serializer._to_dict(coffe_shop)
        result = self.collection.replace_one({"id": coffe_shop.get('id')}, data, upsert=True)
        print(f"Modified count: {result.modified_count}")
        return coffe_shop

    def get_coffe_shop_by_id(self, coffe_shop_id):
        data = self.collection.find_one({"id": coffe_shop_id})
        if data:
            return self.serializer._from_dict(data)
        return None

    def find_many(self, filter_query=None, skip=0, limit=10):
        filter_query = filter_query or {}
        cursor = self.collection.find(filter_query).skip(skip).limit(limit)
        items = [self.serializer._from_dict({k: v for k, v in doc.items() if k != "_id"}) for doc in cursor]
        total = self.collection.count_documents(filter_query)
        return {"results": items, "total": total}

