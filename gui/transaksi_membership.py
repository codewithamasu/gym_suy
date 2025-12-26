import uuid
from datetime import datetime, timedelta
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection


class TransaksiMembership(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)

        self.selected_id = None
        self.create_widgets()
        self.load_combo()
        self.load_data()

    # ================= UI =================
    def create_widgets(self):
        tb.Label(
            self,
            text="Transaksi Membership (Bulanan)",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        form = tb.Frame(self)
        form.pack(pady=10)

        # MEMBER
        tb.Label(form, text="Member").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.member_combo = tb.Combobox(form, state="readonly", width=30)
        self.member_combo.grid(row=0, column=1, padx=5, pady=5)

        # PAKET
        tb.Label(form, text="Paket (Bulan)").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.paket_combo = tb.Combobox(form, state="readonly", width=30)
        self.paket_combo.grid(row=1, column=1, padx=5, pady=5)

        btn = tb.Frame(self)
        btn.pack(pady=10)

        tb.Button(btn, text="Tambah Transaksi", bootstyle=SUCCESS, command=self.insert)\
            .pack(side=LEFT, padx=5)
        tb.Button(btn, text="Hapus", bootstyle=DANGER, command=self.delete)\
            .pack(side=LEFT, padx=5)

        self.tree = ttk.Treeview(
            self,
            columns=("member", "durasi", "mulai", "berakhir"),
            show="headings"
        )
        self.tree.heading("member", text="Member")
        self.tree.heading("durasi", text="Durasi (Bulan)")
        self.tree.heading("mulai", text="Mulai")
        self.tree.heading("berakhir", text="Berakhir")

        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ================= LOAD COMBO =================
    def load_combo(self):
        conn = get_connection()
        cur = conn.cursor()

        # MEMBER (mapping)
        cur.execute("SELECT id, nama FROM members")
        self.member_map = {}
        member_values = []

        for m in cur.fetchall():
            self.member_map[m["nama"]] = m["id"]
            member_values.append(m["nama"])

        self.member_combo["values"] = member_values

        # PAKET MEMBERSHIP (bulanan)
        cur.execute("SELECT id, durasi_bulan FROM paket_membership")
        self.paket_map = {}
        paket_values = []

        for p in cur.fetchall():
            label = f"{p['durasi_bulan']} Bulan"
            self.paket_map[label] = p["id"]
            paket_values.append(label)

        self.paket_combo["values"] = paket_values
        conn.close()

    # ================= LOAD TABLE =================
    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT tm.id, m.nama, p.durasi_bulan,
                   tm.tanggal_mulai, tm.tanggal_berakhir
            FROM transaksi_membership tm
            JOIN members m ON tm.member_id = m.id
            JOIN paket_membership p ON tm.paket_id = p.id
            ORDER BY tm.tanggal_mulai DESC
        """)

        for r in cur.fetchall():
            self.tree.insert(
                "",
                END,
                iid=r["id"],
                values=(
                    r["nama"],
                    r["durasi_bulan"],
                    r["tanggal_mulai"],
                    r["tanggal_berakhir"]
                )
            )
        conn.close()

    # ================= LOGIC =================
    def insert(self):
        member_label = self.member_combo.get()
        paket_label = self.paket_combo.get()

        if not member_label or not paket_label:
            messagebox.showwarning("Validasi", "Member dan paket wajib dipilih")
            return

        member_id = self.member_map.get(member_label)
        paket_id = self.paket_map.get(paket_label)

        if not member_id or not paket_id:
            messagebox.showerror("Error", "Data member atau paket tidak valid")
            return

        conn = get_connection()
        cur = conn.cursor()

        # Ambil durasi paket
        cur.execute("""
            SELECT durasi_bulan FROM paket_membership WHERE id = ?
        """, (paket_id,))
        paket = cur.fetchone()

        if not paket:
            messagebox.showerror("Error", "Paket tidak ditemukan")
            conn.close()
            return

        today = datetime.now().date()
        end_date = today + timedelta(days=paket["durasi_bulan"] * 30)

        cur.execute("""
            INSERT INTO transaksi_membership
            (id, member_id, paket_id, tanggal_mulai, tanggal_berakhir)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            member_id,
            paket_id,
            today.isoformat(),
            end_date.isoformat()
        ))

        conn.commit()
        conn.close()
        self.load_data()

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("Pilih Data", "Pilih transaksi dulu")
            return

        if not messagebox.askyesno("Konfirmasi", "Hapus transaksi ini?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM transaksi_membership WHERE id = ?",
            (self.selected_id,)
        )
        conn.commit()
        conn.close()
        self.load_data()

    def on_select(self, _):
        sel = self.tree.selection()
        if sel:
            self.selected_id = sel[0]
