from datetime import datetime, date
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection


class DashboardMember(tb.Frame):
    def __init__(self, root, member_id):
        super().__init__(root)
        self.root = root
        self.member_id = member_id
        self.pack(fill=BOTH, expand=True)

        self.create_widgets()
        self.load_info()
        self.load_absensi()

    # ================= UI =================
    def create_widgets(self):
        tb.Label(
            self,
            text="Dashboard Member",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=10)

        self.info_label = tb.Label(self, text="", font=("Segoe UI", 11))
        self.info_label.pack(pady=5)

        btn = tb.Frame(self)
        btn.pack(pady=10)

        tb.Button(btn, text="Clock In", bootstyle=SUCCESS, command=self.clock_in)\
            .pack(side=LEFT, padx=5)

        tb.Button(btn, text="Clock Out", bootstyle=WARNING, command=self.clock_out)\
            .pack(side=LEFT, padx=5)
        
        rows = self.load_kelas_saya()
        text = "\n".join([f"{r['nama_kelas']} | {r['tanggal_kelas']} {r['jam_kelas']} | {r['trainer']}" for r in rows])
        tb.Label(self, text=f"Kelas Saya:\n{text}", justify=LEFT).pack(pady=5)

        self.tree = ttk.Treeview(
            self,
            columns=("tanggal", "masuk", "keluar"),
            show="headings"
        )
        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("masuk", text="Jam Masuk")
        self.tree.heading("keluar", text="Jam Keluar")
        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # ================= LOAD =================
    def load_info(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT nama FROM members WHERE id = ?", (self.member_id,))
        name = cur.fetchone()["nama"]

        cur.execute("""
            SELECT tanggal_mulai, tanggal_berakhir
            FROM transaksi_membership
            WHERE member_id = ?
            ORDER BY tanggal_mulai DESC
            LIMIT 1
        """, (self.member_id,))

        trx = cur.fetchone()
        conn.close()

        self.info_label.config(
            text=f"Nama: {name}\n"
                 f"Membership: {trx['tanggal_mulai']} s/d {trx['tanggal_berakhir']}"
        )

    def load_absensi(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT tanggal, jam_masuk, jam_keluar
            FROM absensi
            WHERE member_id = ?
            ORDER BY tanggal DESC
        """, (self.member_id,))

        for r in cur.fetchall():
            self.tree.insert(
                "",
                END,
                values=(r["tanggal"], r["jam_masuk"], r["jam_keluar"])
            )

        conn.close()

    def load_kelas_saya(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT k.nama_kelas, k.tanggal_kelas, k.jam_kelas, t.nama AS trainer
            FROM member_kelas mk
            JOIN kelas k ON mk.kelas_id = k.id
            JOIN trainers t ON k.trainer_id = t.id
            WHERE mk.member_id = ?
            ORDER BY k.tanggal_kelas
        """, (self.member_id,))
        rows = cur.fetchall()
        conn.close()
        return rows


    # ================= ACTION =================
    def clock_in(self):
        today = date.today().isoformat()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 1 FROM absensi
            WHERE member_id = ? AND tanggal = ?
        """, (self.member_id, today))

        if cur.fetchone():
            messagebox.showinfo("Info", "Sudah clock in hari ini")
            conn.close()
            return

        now = datetime.now()
        cur.execute("""
            INSERT INTO absensi (id, member_id, tanggal, jam_masuk)
            VALUES (?, ?, ?, ?)
        """, (
            f"ABS-{now.timestamp()}",
            self.member_id,
            today,
            now.strftime("%H:%M:%S")
        ))

        conn.commit()
        conn.close()
        self.load_absensi()

    def clock_out(self):
        today = date.today().isoformat()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, jam_keluar
            FROM absensi
            WHERE member_id = ? AND tanggal = ?
        """, (self.member_id, today))

        row = cur.fetchone()
        if not row:
            messagebox.showwarning("Info", "Belum clock in hari ini")
            conn.close()
            return

        if row["jam_keluar"]:
            messagebox.showinfo("Info", "Sudah clock out")
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
