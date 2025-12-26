from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection
from utils.auth import verify_password
from .dashboard import Dashboard              # Admin dashboard
from .dashboard_member import DashboardMember # Member dashboard


class Login(tb.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.pack(fill=BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        tb.Label(
            self,
            text="Login",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=20)

        form = tb.Frame(self)
        form.pack(pady=10)

        tb.Label(form, text="Username").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tb.Entry(form, width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        tb.Label(form, text="Password").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tb.Entry(form, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        tb.Button(
            self,
            text="Login",
            bootstyle=SUCCESS,
            command=self.login
        ).pack(pady=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Validasi", "Username dan password wajib diisi")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, password, role
            FROM users
            WHERE username = ?
        """, (username,))
        row = cur.fetchone()
        conn.close()

        if not row or not verify_password(password, row["password"]):
            messagebox.showerror("Gagal", "Username atau password salah")
            return

        # Sukses login → route berdasarkan role
        self.destroy()
        if row["role"] == "ADMIN":
            Dashboard(self.root)
        else:
            # MEMBER: users.id == members.id
            DashboardMember(self.root, row["id"])
