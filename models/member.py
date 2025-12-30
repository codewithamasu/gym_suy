from .user import User

class Member(User):
    def __init__(self, user_id, username, password_hash, membership_end):
        super().__init__(user_id, username, password_hash, "MEMBER")
        self.__membership_end = membership_end

    @property
    def membership_end(self):
        return self.__membership_end

    def is_active(self, today):
        return today <= self.__membership_end

    def get_welcome_message(self):
        return f"Hi Member {self.username}! Ready to workout today?"

    def get_role_description(self):
        # Override: Menjelaskan hak akses Member
        status = "Aktif" if self.__membership_end else "Non-Aktif"
        return f"Member Gym: Akses Fasilitas & Kelas (Status: {status})"
