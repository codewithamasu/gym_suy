from datetime import date
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection
from .dashboard_member import DashboardMember

class LoginMember(tb.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.pack(fill=BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        tb.Label(
            self,
            text="Login Member",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=20)

        form = tb.Frame(self)
        form.pack(pady=10)

        tb.Label(form, text="Pilih Nama Member").grid(row=0, column=0, padx=5, pady=5)
        self.member_combo = tb.Combobox(form, state="readonly", width=30)
        self.member_combo.grid(row=0, column=1, padx=5, pady=5)

        tb.Button(
            self,
            text="Login",
            bootstyle=SUCCESS,
            command=self.login
        ).pack(pady=10)

        self.load_members()

    def load_members(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nama FROM members")

        self.member_map = {}
        values = []

        for m in cur.fetchall():
            self.member_map[m["nama"]] = m["id"]
            values.append(m["nama"])

        self.member_combo["values"] = values
        conn.close()

    def login(self):
        name = self.member_combo.get()
        if not name:
            messagebox.showwarning("Validasi", "Pilih member")
            return

        member_id = self.member_map.get(name)
        today = date.today().isoformat()

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT tanggal_mulai, tanggal_berakhir
            FROM transaksi_membership
            WHERE member_id = ?
            AND ? BETWEEN tanggal_mulai AND tanggal_berakhir
        """, (member_id, today))

        trx = cur.fetchone()
        conn.close()

        if not trx:
            messagebox.showerror("Ditolak", "Membership tidak aktif")
            return

        self.destroy()
        DashboardMember(self.root, member_id)
