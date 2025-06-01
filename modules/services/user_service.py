# -*- coding: utf-8 -*-
from modules.models.user import User
from modules.repository.user_repository import UserRepository
from modules.services.coffee_shop_service import CoffeeShopService

class UserService:
    def __init__(self, user_repository=None, coffee_shop_service=None):
        if user_repository is None:
            user_repository = UserRepository(uri="mongodb://localhost:27017", db_name="my_database")
        self.user_repository = user_repository
        if coffee_shop_service is None:
            coffee_shop_service = CoffeeShopService()
        self.coffee_shop_service = coffee_shop_service

    def register_user(self, username, password, phone, email, region):
        if self.user_repository.get_user_by_username(username) is not None:
            raise ValueError("Пользователь с таким именем уже существует")
        new_user = User(username, password, phone, email, region)
        print("new User")
        self.user_repository.add_user(new_user)
        return new_user

    def login_user(self, username, password):
        user = self.user_repository.get_user_by_username(username)
        if user and user.password == password:
            return user
        return None

    def add_favorite(self, user_id, coffee_shop: dict):
        self.coffee_shop_service.add_or_update_coffee_shop(coffee_shop)

        user = self.user_repository.get_user_by_id(user_id)
        print(f"User = {user}")
        coffee_id = coffee_shop.get("id")
        print(f"User favorites = {user.favorites}")
        if any(shop["id"] == coffee_id for shop in user.favorites):
            return False

        user.favorites.append({
            "id": coffee_id,
            "user_tags": []
        })

        self.user_repository.update_user(user)
        return True


    def add_tag_to_favorite(self, user_id, coffee_shop_id, new_tag):
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")

        for favorite in user.favorites:
            if favorite.get("id") == coffee_shop_id:
                if new_tag in favorite.get("user_tags", []):
                    raise ValueError("Такой тэг уже существует")
                favorite["user_tags"].append(new_tag)
                self.user_repository.update_user(user)
                return user

        raise ValueError("Кофейня не найдена в избранном")

    def remove_tag_from_favorite(self, user_id, coffee_shop_id, tag_to_remove):
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")

        for favorite in user.favorites:
            if favorite.get("id") == coffee_shop_id:
                user_tags = favorite.get("user_tags", [])
                if tag_to_remove not in user_tags:
                    raise ValueError("У пользователя нет такого тега для этой кофейни")
                user_tags.remove(tag_to_remove)
                self.user_repository.update_user(user)
                return True

        raise ValueError("Кофейня не найдена в избранном")


    def add_friend(self, user_id, friend_name):
        user = self.user_repository.get_user_by_id(user_id)
        if friend_name not in user.friends:
            user.friends.append(friend_name)
            self.user_repository.update_user(user)
        return user

    def get_user_by_username(self, username):
        return self.user_repository.get_user_by_username(username)

    def get_user_by_id(self, user_id):
        return self.user_repository.get_user_by_id(user_id)

    def user_exists(self, username):
        return self.user_repository.get_user_by_username(username) is not None
