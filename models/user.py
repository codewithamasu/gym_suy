import bcrypt


class User:
    def __init__(self, user_id, username, password_hash, role):
        self.__id = user_id
        self.__username = username
        self.__password_hash = password_hash  # sudah di-hash bcrypt
        self.__role = role

    # ================= GETTER =================
    @property
    def id(self):
        return self.__id

    @property
    def username(self):
        return self.__username

    @property
    def role(self):
        return self.__role

    # ================= SECURITY =================
    def check_password(self, plain_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            self.__password_hash.encode("utf-8")
        )

    # ================= POLYMORPHISM =================
    def get_role_description(self):
        """
        Contoh Polimorfisme pada Business Logic (Model).
        Setiap role memberikan deskripsi hak akses yang berbeda.
        """
        return "Pengguna Umum"
