from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection
from utils.auth import verify_password
from .dashboard import Dashboard
from .dashboard_member import DashboardMember

from PIL import Image, ImageTk, ImageFilter
import os


class Login(tb.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.pack(fill=BOTH, expand=True)

        self.bg_img = None
        self.load_background()
        self.create_layout()

    # ================= BACKGROUND =================
    def load_background(self):
        img_path = os.path.join("assets", "bg_login_2.jpg")

        img = Image.open(img_path)
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        img = img.resize((w, h), Image.LANCZOS)
        img = img.filter(ImageFilter.GaussianBlur(10))

        self.bg_img = ImageTk.PhotoImage(img)
        bg = tb.Label(self, image=self.bg_img)
        bg.place(relx=0, rely=0, relwidth=1, relheight=1)

    # ================= LAYOUT =================
    def create_layout(self):
        # Container utama (CENTER)
        main = tb.Frame(self)
        main.place(relx=0.5, rely=0.5, anchor=CENTER)

        # Card Login
        card = tb.Frame(
            main,
            padding=30,
            bootstyle="light"
        )
        card.pack()

        tb.Label(
            card,
            text="Gym Management System",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(0, 5))

        tb.Label(
            card,
            text="Admin / Member Login",
            font=("Segoe UI", 11),
            foreground="#666"
        ).pack(pady=(0, 20))

        tb.Label(card, text="Username").pack(anchor=W)
        self.username_entry = tb.Entry(card, width=30)
        self.username_entry.pack(pady=(5, 15))

        tb.Label(card, text="Password").pack(anchor=W)
        self.password_entry = tb.Entry(card, width=30, show="•")
        self.password_entry.pack(pady=(5, 20))

        tb.Button(
            card,
            text="Sign In",
            bootstyle=PRIMARY,
            width=25,
            command=self.login
        ).pack(pady=(5, 10))


    # ================= LOGIN LOGIC =================
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

        self.destroy()
        if row["role"] == "ADMIN":
            Dashboard(self.root)
        else:
            DashboardMember(self.root, row["id"])
