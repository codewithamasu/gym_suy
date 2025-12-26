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
    # ================= UI =================
    def create_widgets(self):
        # HEADER
        header_frame = tb.Frame(self)
        header_frame.pack(fill=X, padx=20, pady=20)
        tb.Label(
            header_frame,
            text="Registrasi Membership Baru",
            font=("Helvetica", 18, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)

        # FORM CONTAINER
        form_frame = tb.Labelframe(self, text="Form Transaksi", padding=20, bootstyle="primary")
        form_frame.pack(fill=X, padx=20, pady=5)
        
        form_frame.columnconfigure(1, weight=1)

        # MEMBER
        tb.Label(form_frame, text="Pilih Member:").grid(row=0, column=0, sticky=W, padx=10, pady=10)
        self.member_combo = tb.Combobox(form_frame, state="readonly")
        self.member_combo.grid(row=0, column=1, sticky=EW, padx=10)

        # PAKET
        tb.Label(form_frame, text="Pilih Paket:").grid(row=1, column=0, sticky=W, padx=10, pady=10)
        self.paket_combo = tb.Combobox(form_frame, state="readonly")
        self.paket_combo.grid(row=1, column=1, sticky=EW, padx=10)

        # BUTTONS
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill=X, padx=20, pady=20)
        
        tb.Button(btn_frame, text="Buat Transaksi", bootstyle="success", command=self.insert).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Hapus Data", bootstyle="danger", command=self.delete).pack(side=LEFT, padx=5)

        # TABLE
        tree_frame = tb.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        y_scroll = tb.Scrollbar(tree_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("member", "durasi", "mulai", "berakhir"),
            show="headings",
            yscrollcommand=y_scroll.set,
            style="primary.Treeview"
        )
        y_scroll.config(command=self.tree.yview)

        self.tree.heading("member", text="Member")
        self.tree.heading("durasi", text="Durasi (Bulan)")
        self.tree.heading("mulai", text="Tanggal Mulai")
        self.tree.heading("berakhir", text="Tanggal Berakhir")
        
        self.tree.column("member", width=200)
        self.tree.column("durasi", width=100)
        
        self.tree.pack(fill=BOTH, expand=True)
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
