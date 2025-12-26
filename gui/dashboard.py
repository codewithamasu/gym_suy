import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import Frame, Label
from database.db import get_connection
from .master_member import MasterMember
from .master_trainer import MasterTrainer
from .master_paket import MasterPaket
from .transaksi_membership import TransaksiMembership
from .absensi import Absensi
from .pembayaran import Pembayaran
from .transaksi_harian import TransaksiHarian
from .master_kelas import MasterKelas
from .member_kelas import MemberKelas

class Dashboard:
    def __init__(self, root):
        self.root = root

        self.sidebar = Frame(root, bg="#2c3e50", width=220)
        self.sidebar.pack(side=LEFT, fill=Y)

        self.content = Frame(root, bg="#ecf0f1")
        self.content.pack(side=RIGHT, fill=BOTH, expand=True)

        self.create_sidebar()
        self.show_dashboard()

    # ================= SIDEBAR =================
    def create_sidebar(self):
        Label(
            self.sidebar,
            text="GYM SYSTEM",
            bg="#2c3e50",
            fg="white",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=20)

        self.create_button("Dashboard", self.show_dashboard)
        self.create_button("Member", self.show_member)
        self.create_button("Kelas", self.show_kelas)
        self.create_button("Member Ambil Kelas", self.show_member_kelas)
        self.create_button("Trainer", self.show_trainer)
        self.create_button("Paket", self.show_paket)
        self.create_button("Alat Gym", self.show_alat)

        Label(self.sidebar, bg="#2c3e50").pack(pady=10)

        self.create_button("Transaksi Membership", self.show_transaksi_membership)
        self.create_button("Transaksi Harian", self.show_transaksi_harian)
        self.create_button("Transaksi Kelas", self.show_transaksi_kelas)
        self.create_button("Pembayaran", self.show_pembayaran)
        self.create_button("Absensi", self.show_absensi)

    def create_button(self, text, command):
        tb.Button(
            self.sidebar,
            text=text,
            bootstyle="secondary",
            width=25,
            command=command
        ).pack(pady=5)

    # ================= CONTENT HANDLER =================
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_title(self, title):
        Label(
            self.content,
            text=title,
            font=("Segoe UI", 16, "bold"),
            bg="#ecf0f1"
        ).pack(pady=20)

    # ================= PAGES =================
    def show_dashboard(self):
        self.clear_content()
        self.show_title("Dashboard")

        Label(
            self.content,
            text="Selamat datang di Sistem Manajemen Gym",
            font=("Segoe UI", 11),
            bg="#ecf0f1"
        ).pack()

    def show_member(self):
        self.clear_content()
        MasterMember(self.content)

    def show_trainer(self):
        self.clear_content()
        MasterTrainer(self.content)

    def show_paket(self):
        self.clear_content()
        MasterPaket(self.content)

    def show_transaksi_harian(self):
        self.clear_content()
        TransaksiHarian(self.content)

    def show_kelas(self):
        self.clear_content()
        MasterKelas(self.content)

    def show_alat(self):
        self.clear_content()
        self.show_title("Master Alat Gym")

    def show_transaksi_membership(self):
        self.clear_content()
        TransaksiMembership(self.content)

    def show_transaksi_kelas(self):
        self.clear_content()
        self.show_title("Transaksi Kelas")

    def show_pembayaran(self):
        self.clear_content()
        Pembayaran(self.content)

    def show_absensi(self):
        self.clear_content()
        self.show_title("Absensi Member")

        tree = tb.Treeview(
            self.content,
            columns=("member", "tanggal", "masuk", "keluar"),
            show="headings"
        )

        tree.heading("member", text="Member")
        tree.heading("tanggal", text="Tanggal")
        tree.heading("masuk", text="Jam Masuk")
        tree.heading("keluar", text="Jam Keluar")

        tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT m.nama, a.tanggal, a.jam_masuk, a.jam_keluar
            FROM absensi a
            JOIN members m ON a.member_id = m.id
            ORDER BY a.tanggal DESC, a.jam_masuk DESC
        """)

        for r in cur.fetchall():
            tree.insert(
                "",
                END,
                values=(
                    r["nama"],
                    r["tanggal"],
                    r["jam_masuk"],
                    r["jam_keluar"]
                )
            )

        conn.close()

    def show_member_kelas(self):
        self.clear_content()
        MemberKelas(self.content)


