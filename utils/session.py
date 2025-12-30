class SessionManager:
    # Private variable to store current user
    __current_user = None

    @classmethod
    def set_user(cls, user):

        cls.__current_user = user

    @classmethod
    def get_user(cls):
        return cls.__current_user

    @classmethod
    def clear_session(cls):
        cls.__current_user = None
