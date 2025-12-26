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
        # Container untuk centering
        container = tb.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor=CENTER)

        # Card Frame (Untuk efek border/bg)
        card = tb.Frame(container, bootstyle="secondary", padding=30)
        card.pack()

        # Title
        tb.Label(
            card,
            text="GYM MANAGEMEN SYSTEM",
            font=("Helvetica", 24, "bold"),
            bootstyle="inverse-secondary"
        ).pack(pady=(0, 20))

        tb.Label(
            card,
            text="Login Area",
            font=("Helvetica", 12),
            bootstyle="inverse-secondary"
        ).pack(pady=(0, 20))

        # Form
        form = tb.Frame(card, bootstyle="secondary")
        form.pack(pady=10)

        # Username
        username_frame = tb.Frame(form, bootstyle="secondary")
        username_frame.pack(fill=X, pady=5)
        tb.Label(
            username_frame, 
            text="Username", 
            bootstyle="inverse-secondary",
            font=("Helvetica", 10)
        ).pack(anchor=W)
        self.username_entry = tb.Entry(username_frame, width=35, font=("Helvetica", 10))
        self.username_entry.pack(pady=(5, 0))

        # Password
        password_frame = tb.Frame(form, bootstyle="secondary")
        password_frame.pack(fill=X, pady=10)
        tb.Label(
            password_frame, 
            text="Password", 
            bootstyle="inverse-secondary",
            font=("Helvetica", 10)
        ).pack(anchor=W)
        self.password_entry = tb.Entry(
            password_frame, 
            width=35, 
            show="•", 
            font=("Helvetica", 10)
        )
        self.password_entry.pack(pady=(5, 0))

        # Button
        tb.Button(
            card,
            text="LOGIN",
            bootstyle="primary",
            width=20,
            command=self.login
        ).pack(pady=20)

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
