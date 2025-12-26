import uuid
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection


class MasterPaket(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)

        self.selected_id = None
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        tb.Label(
            self,
            text="Master Paket Membership (Bulanan)",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        form = tb.Frame(self)
        form.pack(pady=10)

        tb.Label(form, text="Durasi (Bulan)").grid(row=0, column=0, sticky=W, padx=5)
        self.durasi_combo = tb.Combobox(
            form,
            values=[1, 2, 3, 6, 12],
            state="readonly",
            width=28
        )
        self.durasi_combo.grid(row=0, column=1, padx=5)
        self.durasi_combo.set(1)
        self.durasi_combo.bind("<<ComboboxSelected>>", self.update_harga)

        tb.Label(form, text="Harga").grid(row=1, column=0, sticky=W, padx=5)
        self.harga_entry = tb.Entry(form, width=30, state="readonly")
        self.harga_entry.grid(row=1, column=1, padx=5)

        self.update_harga()

        btn = tb.Frame(self)
        btn.pack(pady=10)

        tb.Button(btn, text="Tambah", bootstyle=SUCCESS, command=self.insert).pack(side=LEFT, padx=5)
        tb.Button(btn, text="Update", bootstyle=WARNING, command=self.update).pack(side=LEFT, padx=5)
        tb.Button(btn, text="Hapus", bootstyle=DANGER, command=self.delete).pack(side=LEFT, padx=5)
        tb.Button(btn, text="Reset", bootstyle=SECONDARY, command=self.reset).pack(side=LEFT, padx=5)

        self.tree = ttk.Treeview(
            self,
            columns=("durasi", "harga"),
            show="headings"
        )
        self.tree.heading("durasi", text="Durasi (Bulan)")
        self.tree.heading("harga", text="Harga")
        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def update_harga(self, _=None):
        durasi = int(self.durasi_combo.get())
        harga = durasi * 200000
        self.harga_entry.config(state="normal")
        self.harga_entry.delete(0, END)
        self.harga_entry.insert(0, harga)
        self.harga_entry.config(state="readonly")

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM paket_membership")
        for r in cur.fetchall():
            self.tree.insert(
                "",
                END,
                iid=r["id"],
                values=(r["durasi_bulan"], r["harga"])
            )
        conn.close()

    def insert(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO paket_membership (id, durasi_bulan, harga)
            VALUES (?, ?, ?)
        """, (
            str(uuid.uuid4()),
            int(self.durasi_combo.get()),
            int(self.harga_entry.get())
        ))
        conn.commit()
        conn.close()
        self.load_data()
        self.reset()

    def update(self):
        if not self.selected_id:
            messagebox.showwarning("Pilih Data", "Pilih paket terlebih dahulu")
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE paket_membership
            SET durasi_bulan = ?, harga = ?
            WHERE id = ?
        """, (
            int(self.durasi_combo.get()),
            int(self.harga_entry.get()),
            self.selected_id
        ))
        conn.commit()
        conn.close()
        self.load_data()
        self.reset()

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("Pilih Data", "Pilih paket terlebih dahulu")
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM paket_membership WHERE id = ?", (self.selected_id,))
        conn.commit()
        conn.close()
        self.load_data()
        self.reset()

    def on_select(self, _):
        sel = self.tree.selection()
        if sel:
            self.selected_id = sel[0]
            durasi, harga = self.tree.item(self.selected_id, "values")
            self.durasi_combo.set(durasi)
            self.update_harga()

    def reset(self):
        self.selected_id = None
        self.durasi_combo.set(1)
        self.update_harga()
