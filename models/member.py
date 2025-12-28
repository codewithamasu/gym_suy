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
