# # -*- coding: utf-8 -*-

# class InMemoryRepository:
#     def __init__(self):
#         self.users = {}

#     def add_user(self, user):
#         self.users[user.id] = user
#         return user

#     def get_user_by_id(self, user_id):
#         return self.users.get(user_id)

#     def get_user_by_username(self, username):
#         for user in self.users.values():
#             if user.username == username:
#                 return user
#         return None

# -*- coding: utf-8 -*-

class InMemoryRepository:
    def __init__(self):
        # Словарь для хранения пользователей: ключ – уникальный идентификатор, значение – объект User.
        self.users = {}

    def add_user(self, user):
        """
        Добавляет пользователя в репозиторий.

        :param user: Объект пользователя, который должен иметь уникальное свойство 'id'.
        :return: Добавленный объект пользователя.
        """
        self.users[user.id] = user
        return user

    def get_user_by_username(self, username):
        """
        Ищет пользователя по имени.

        :param username: Строка с именем пользователя.
        :return: Объект пользователя, если пользователь найден, иначе None.
        """
        for user in self.users.values():
            if user.username == username:
                return user
        return None
