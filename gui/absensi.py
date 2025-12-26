from datetime import datetime, date
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection


class Absensi(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)

        self.create_widgets()
        self.load_members()
        self.load_absensi()

    # ================= UI =================
    def create_widgets(self):
        tb.Label(
            self,
            text="Absensi Member",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        form = tb.Frame(self)
        form.pack(pady=10)

        tb.Label(form, text="Member").grid(row=0, column=0, sticky=W, padx=5)
        self.member_combo = tb.Combobox(form, state="readonly", width=30)
        self.member_combo.grid(row=0, column=1, padx=5)

        btn = tb.Frame(self)
        btn.pack(pady=10)

        tb.Button(
            btn, text="Clock In", bootstyle=SUCCESS, command=self.clock_in
        ).pack(side=LEFT, padx=5)

        tb.Button(
            btn, text="Clock Out", bootstyle=WARNING, command=self.clock_out
        ).pack(side=LEFT, padx=5)

        self.tree = ttk.Treeview(
            self,
            columns=("member", "tanggal", "masuk", "keluar"),
            show="headings"
        )
        self.tree.heading("member", text="Member")
        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("masuk", text="Jam Masuk")
        self.tree.heading("keluar", text="Jam Keluar")

        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # ================= LOAD =================
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

    def load_absensi(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT a.id, m.nama, a.tanggal, a.jam_masuk, a.jam_keluar
            FROM absensi a
            JOIN members m ON a.member_id = m.id
            ORDER BY a.tanggal DESC
        """)

        for r in cur.fetchall():
            self.tree.insert(
                "",
                END,
                iid=r["id"],
                values=(r["nama"], r["tanggal"], r["jam_masuk"], r["jam_keluar"])
            )
        conn.close()

    # ================= VALIDASI =================
    def has_active_membership(self, member_id):
        today = date.today().isoformat()
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 1 FROM transaksi_membership
            WHERE member_id = ?
            AND ? BETWEEN tanggal_mulai AND tanggal_berakhir
        """, (member_id, today))

        active = cur.fetchone() is not None
        conn.close()
        return active

    def has_clocked_in_today(self, member_id):
        today = date.today().isoformat()
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id FROM absensi
            WHERE member_id = ? AND tanggal = ?
        """, (member_id, today))

        row = cur.fetchone()
        conn.close()
        return row

    # ================= ACTION =================
    def clock_in(self):
        member_name = self.member_combo.get()
        if not member_name:
            messagebox.showwarning("Validasi", "Pilih member")
            return

        member_id = self.member_map.get(member_name)

        if not self.has_active_membership(member_id):
            messagebox.showerror("Ditolak", "Membership tidak aktif")
            return

        if self.has_clocked_in_today(member_id):
            messagebox.showwarning("Info", "Member sudah clock in hari ini")
            return

        now = datetime.now()
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO absensi (id, member_id, tanggal, jam_masuk)
            VALUES (?, ?, ?, ?)
        """, (
            f"ABS-{now.timestamp()}",
            member_id,
            now.date().isoformat(),
            now.strftime("%H:%M:%S")
        ))

        conn.commit()
        conn.close()
        self.load_absensi()

    def clock_out(self):
        member_name = self.member_combo.get()
        if not member_name:
            messagebox.showwarning("Validasi", "Pilih member")
            return

        member_id = self.member_map.get(member_name)
        today = date.today().isoformat()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, jam_keluar FROM absensi
            WHERE member_id = ? AND tanggal = ?
        """, (member_id, today))

        row = cur.fetchone()
        if not row:
            messagebox.showwarning("Info", "Belum clock in hari ini")
            conn.close()
            return

        if row["jam_keluar"]:
            messagebox.showwarning("Info", "Sudah clock out")
            conn.close()
            return

        cur.execute("""
            UPDATE absensi
            SET jam_keluar = ?
            WHERE id = ?
        """, (
            datetime.now().strftime("%H:%M:%S"),
            row["id"]
        ))

        conn.commit()
        conn.close()
        self.load_absensi()
