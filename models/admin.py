from .user import User

class Admin(User):
    def __init__(self, user_id, username, password_hash):
        super().__init__(user_id, username, password_hash, "ADMIN")

    def can_manage_system(self):
        return True

    def get_welcome_message(self):
        return f"Welcome Administrator {self.username}. System is ready."

    def get_role_description(self):
        # Override: Menjelaskan hak akses Admin
        return "Administrator: Akses Penuh ke Data Master & Laporan"
