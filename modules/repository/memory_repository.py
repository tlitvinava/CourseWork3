# # -*- coding: utf-8 -*-

class InMemoryRepository:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(InMemoryRepository, cls).__new__(cls)
            cls.instance.sessions = {}
        return cls.instance

    def save(self, session_id, username):
        self.sessions[session_id] = username

    def get_username(self, session_id):
        return self.sessions.get(session_id)

    def delete(self, session_id):
        self.sessions.pop(session_id, None)
