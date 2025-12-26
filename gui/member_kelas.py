import uuid
from datetime import date
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection


class MemberKelas(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)

        self.member_map = {}
        self.kelas_map = {}
        self.selected_id = None

        self.create_widgets()
        self.load_members()
        self.load_kelas()
        self.load_data()

    # ================= UI =================
    def create_widgets(self):
        tb.Label(self, text="Pendaftaran Kelas (Member)", font=("Segoe UI", 16, "bold")).pack(pady=10)

        form = tb.Frame(self)
        form.pack(pady=10)

        tb.Label(form, text="Member").grid(row=0, column=0, sticky=W, padx=5)
        self.member_combo = tb.Combobox(form, state="readonly", width=30)
        self.member_combo.grid(row=0, column=1, padx=5)

        tb.Label(form, text="Kelas").grid(row=1, column=0, sticky=W, padx=5)
        self.kelas_combo = tb.Combobox(form, state="readonly", width=30)
        self.kelas_combo.grid(row=1, column=1, padx=5)

        btn = tb.Frame(self)
        btn.pack(pady=10)

        tb.Button(btn, text="Daftarkan", bootstyle=SUCCESS, command=self.insert).pack(side=LEFT, padx=5)
        tb.Button(btn, text="Hapus", bootstyle=DANGER, command=self.delete).pack(side=LEFT, padx=5)

        self.tree = ttk.Treeview(
            self,
            columns=("member", "kelas", "tanggal"),
            show="headings"
        )
        self.tree.heading("member", text="Member")
        self.tree.heading("kelas", text="Kelas")
        self.tree.heading("tanggal", text="Tanggal Daftar")
        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ================= LOAD =================
    def load_members(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nama FROM members")
        self.member_map = {r["nama"]: r["id"] for r in cur.fetchall()}
        self.member_combo["values"] = list(self.member_map.keys())
        conn.close()

    def load_kelas(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT k.id, k.nama_kelas, k.tanggal_kelas, k.jam_kelas,
                   k.kapasitas,
                   COUNT(mk.id) AS terdaftar
            FROM kelas k
            LEFT JOIN member_kelas mk ON mk.kelas_id = k.id
            GROUP BY k.id
        """)
        self.kelas_map = {}
        values = []
        for r in cur.fetchall():
            sisa = r["kapasitas"] - r["terdaftar"]
            label = f"{r['nama_kelas']} ({r['tanggal_kelas']} {r['jam_kelas']}) | Sisa {sisa}"
            self.kelas_map[label] = r["id"]
            values.append(label)
        self.kelas_combo["values"] = values
        conn.close()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT mk.id, m.nama AS member, k.nama_kelas AS kelas, mk.tanggal_daftar
            FROM member_kelas mk
            JOIN members m ON mk.member_id = m.id
            JOIN kelas k ON mk.kelas_id = k.id
            ORDER BY mk.tanggal_daftar DESC
        """)
        for r in cur.fetchall():
            self.tree.insert("", END, iid=r["id"], values=(r["member"], r["kelas"], r["tanggal_daftar"]))
        conn.close()

    # ================= ACTION =================
    def insert(self):
        member_name = self.member_combo.get()
        kelas_label = self.kelas_combo.get()
        if not member_name or not kelas_label:
            messagebox.showwarning("Validasi", "Pilih member dan kelas")
            return

        member_id = self.member_map[member_name]
        kelas_id = self.kelas_map[kelas_label]

        conn = get_connection()
        cur = conn.cursor()

        # Cek kapasitas
        cur.execute("""
            SELECT k.kapasitas, COUNT(mk.id) AS terdaftar
            FROM kelas k
            LEFT JOIN member_kelas mk ON mk.kelas_id = k.id
            WHERE k.id = ?
            GROUP BY k.id
        """, (kelas_id,))
        row = cur.fetchone()
        if row and row["terdaftar"] >= row["kapasitas"]:
            conn.close()
            messagebox.showerror("Penuh", "Kapasitas kelas sudah penuh")
            return

        try:
            cur.execute("""
                INSERT INTO member_kelas (id, member_id, kelas_id, tanggal_daftar)
                VALUES (?, ?, ?, ?)
            """, (str(uuid.uuid4()), member_id, kelas_id, date.today().isoformat()))
            conn.commit()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Gagal", str(e))
        finally:
            conn.close()

        self.load_kelas()
        self.load_data()

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("Pilih Data", "Pilih data terlebih dahulu")
            return
        if not messagebox.askyesno("Konfirmasi", "Hapus pendaftaran kelas ini?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM member_kelas WHERE id = ?", (self.selected_id,))
        conn.commit()
        conn.close()

        self.load_kelas()
        self.load_data()

    def on_select(self, _):
        sel = self.tree.selection()
        if sel:
            self.selected_id = sel[0]
