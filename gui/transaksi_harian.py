import uuid
from datetime import datetime
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection


HARGA_HARIAN = 20000


class TransaksiHarian(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)

        self.create_widgets()
        self.load_data()

    # ================= UI =================
    def create_widgets(self):
        tb.Label(
            self,
            text="Transaksi Harian (Non-Member)",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        form = tb.Frame(self)
        form.pack(pady=10)

        tb.Label(form, text="Nama Pengunjung").grid(row=0, column=0, sticky=W, padx=5)
        self.nama_entry = tb.Entry(form, width=30)
        self.nama_entry.grid(row=0, column=1, padx=5)

        tb.Label(form, text="Harga").grid(row=1, column=0, sticky=W, padx=5)
        self.harga_entry = tb.Entry(form, width=30, state="readonly")
        self.harga_entry.grid(row=1, column=1, padx=5)
        self.set_harga()

        btn = tb.Frame(self)
        btn.pack(pady=10)

        tb.Button(
            btn, text="Simpan Transaksi", bootstyle=SUCCESS, command=self.insert
        ).pack(side=LEFT, padx=5)

        self.tree = ttk.Treeview(
            self,
            columns=("nama", "tanggal", "jam", "harga"),
            show="headings"
        )
        self.tree.heading("nama", text="Nama")
        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("jam", text="Jam Masuk")
        self.tree.heading("harga", text="Harga")

        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # ================= LOGIC =================
    def set_harga(self):
        self.harga_entry.config(state="normal")
        self.harga_entry.delete(0, END)
        self.harga_entry.insert(0, HARGA_HARIAN)
        self.harga_entry.config(state="readonly")

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT nama_pengunjung, tanggal, waktu_masuk, harga
            FROM transaksi_harian
            ORDER BY tanggal DESC, waktu_masuk DESC
        """)

        for r in cur.fetchall():
            self.tree.insert(
                "",
                END,
                values=(r["nama_pengunjung"], r["tanggal"], r["waktu_masuk"], r["harga"])
            )

        conn.close()

    def insert(self):
        nama = self.nama_entry.get().strip()
        if not nama:
            messagebox.showwarning("Validasi", "Nama pengunjung wajib diisi")
            return

        now = datetime.now()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO transaksi_harian
            (id, nama_pengunjung, tanggal, harga, waktu_masuk)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            nama,
            now.date().isoformat(),
            HARGA_HARIAN,
            now.strftime("%H:%M:%S")
        ))

        conn.commit()
        conn.close()

        self.nama_entry.delete(0, END)
        self.load_data()
        messagebox.showinfo("Sukses", "Transaksi harian berhasil disimpan")
