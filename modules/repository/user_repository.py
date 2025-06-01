from modules.models.user import User
from modules.repository.mongo_repository import MongoRepository
from TSerializerPack.serializer import UniversalSerializer

class UserRepository(MongoRepository):
    def __init__(self, uri="mongodb://localhost:27017", db_name="my_database"):
        super().__init__(uri, db_name)
        self.collection = self.db["users"]
        self.serializer = UniversalSerializer(User)

    def add_user(self, user):
        print("start ADD USER")
        data = self.serializer._to_dict(user)
        self.collection.insert_one(data)
        return user

    def update_user(self, user):
        print("обновляем юзера")
        data = self.serializer._to_dict(user)
        print(user)
        result = self.collection.replace_one({"id": user.id}, data, upsert=True)
        print(f"Modified count: {result.modified_count}")
        return user

    def get_user_by_username(self, username):
        data = self.collection.find_one({"username": username})
        if data:
            return self.serializer._from_dict(data)
        return None

    def get_user_by_id(self, user_id):
        data = self.collection.find_one({"id": user_id})
        if data:
            return self.serializer._from_dict(data)
        return None

