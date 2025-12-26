import uuid
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection

class MasterTrainer(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)

        self.selected_id = None

        self.create_widgets()
        self.load_data()

    # ================= UI =================
    def create_widgets(self):
        tb.Label(
            self,
            text="Master Trainer",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        # -------- FORM --------
        form = tb.Frame(self)
        form.pack(pady=10)

        tb.Label(form, text="Nama Trainer").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.nama_entry = tb.Entry(form, width=30)
        self.nama_entry.grid(row=0, column=1, padx=5, pady=5)

        tb.Label(form, text="Spesialisasi").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.spesialisasi_combo = tb.Combobox(
            form,
            values=["Strength", "Cardio", "Yoga", "Rehabilitation"],
            state="readonly",
            width=28
        )
        self.spesialisasi_combo.grid(row=1, column=1, padx=5, pady=5)
        self.spesialisasi_combo.set("Strength")


        tb.Label(form, text="Tarif / Sesi").grid(row=2, column=0, sticky=W, padx=5, pady=5)
        self.tarif_entry = tb.Entry(form, width=30)
        self.tarif_entry.grid(row=2, column=1, padx=5, pady=5)

        # -------- BUTTON --------
        btn_frame = tb.Frame(self)
        btn_frame.pack(pady=10)

        tb.Button(btn_frame, text="Tambah", bootstyle=SUCCESS, command=self.insert).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Update", bootstyle=WARNING, command=self.update).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Hapus", bootstyle=DANGER, command=self.delete).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Reset", bootstyle=SECONDARY, command=self.reset_form).pack(side=LEFT, padx=5)

        # -------- TABLE --------
        self.tree = ttk.Treeview(
            self,
            columns=("nama", "spesialisasi", "tarif"),
            show="headings"
        )
        self.tree.heading("nama", text="Nama")
        self.tree.heading("spesialisasi", text="Spesialisasi")
        self.tree.heading("tarif", text="Tarif / Sesi")

        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ================= DATABASE =================
    def load_data(self):
        self.tree.delete(*self.tree.get_children())

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trainers")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert(
                "",
                END,
                iid=row["id"],
                values=(row["nama"], row["spesialisasi"], row["tarif_per_sesi"])
            )

    def insert(self):
        nama = self.nama_entry.get()
        spesialisasi = self.spesialisasi_combo.get()
        tarif = self.tarif_entry.get()

        if not nama or not tarif:
            messagebox.showwarning("Validasi", "Nama dan tarif wajib diisi")
            return

        try:
            tarif = int(tarif)
        except ValueError:
            messagebox.showwarning("Validasi", "Tarif harus angka")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trainers (id, nama, spesialisasi, tarif_per_sesi)
            VALUES (?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            nama,
            self.spesialisasi_combo.get(),
            tarif
        ))
        conn.commit()
        conn.close()

        self.load_data()
        self.reset_form()

    def update(self):
        if not self.selected_id:
            messagebox.showwarning("Pilih Data", "Pilih trainer terlebih dahulu")
            return

        try:
            tarif = int(self.tarif_entry.get())
        except ValueError:
            messagebox.showwarning("Validasi", "Tarif harus angka")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE trainers
            SET nama = ?, spesialisasi = ?, tarif_per_sesi = ?
            WHERE id = ?
        """, (
            self.nama_entry.get(),
            self.spesialisasi_combo.get(),
            tarif,
            self.selected_id
        ))
        conn.commit()
        conn.close()

        self.load_data()
        self.reset_form()

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("Pilih Data", "Pilih trainer terlebih dahulu")
            return

        if not messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus trainer ini?"):
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM trainers WHERE id = ?", (self.selected_id,))
        conn.commit()
        conn.close()

        self.load_data()
        self.reset_form()

    # ================= EVENT =================
    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        self.selected_id = selected[0]
        values = self.tree.item(self.selected_id, "values")

        self.nama_entry.delete(0, END)
        self.nama_entry.insert(0, values[0])

        self.spesialisasi_combo.delete(0, END)
        self.spesialisasi_combo.insert(0, values[1])

        self.tarif_entry.delete(0, END)
        self.tarif_entry.insert(0, values[2])

    def reset_form(self):
        self.selected_id = None
        self.nama_entry.delete(0, END)
        self.spesialisasi_combo.delete(0, END)
        self.tarif_entry.delete(0, END)
