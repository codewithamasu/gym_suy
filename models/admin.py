from .user import User

class Admin(User):
    def __init__(self, user_id, username, password_hash):
        super().__init__(user_id, username, password_hash, "ADMIN")

    def can_manage_system(self):
        return True
