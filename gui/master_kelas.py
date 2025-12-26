import uuid
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from database.db import get_connection


class MasterKelas(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)

        self.selected_id = None
        self.trainer_map = {}

        self.create_widgets()
        self.load_trainers()
        self.load_data()

    # ================= UI =================
    def create_widgets(self):
        tb.Label(
            self,
            text="Master Kelas Gym",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        form = tb.Frame(self)
        form.pack(pady=10)

        tb.Label(form, text="Nama Kelas").grid(row=0, column=0, sticky=W, padx=5)
        self.nama_entry = tb.Entry(form, width=30)
        self.nama_entry.grid(row=0, column=1, padx=5)

        tb.Label(form, text="Trainer").grid(row=1, column=0, sticky=W, padx=5)
        self.trainer_combo = tb.Combobox(form, state="readonly", width=28)
        self.trainer_combo.grid(row=1, column=1, padx=5)

        tb.Label(form, text="Tanggal Kelas").grid(row=2, column=0, sticky=W, padx=5)
        self.tanggal_entry = DateEntry(form, width=27, bootstyle=PRIMARY)
        self.tanggal_entry.grid(row=2, column=1, padx=5)

        tb.Label(form, text="Jam (HH:MM)").grid(row=3, column=0, sticky=W, padx=5)
        self.jam_entry = tb.Entry(form, width=30)
        self.jam_entry.grid(row=3, column=1, padx=5)

        tb.Label(form, text="Kapasitas").grid(row=4, column=0, sticky=W, padx=5)
        self.kapasitas_entry = tb.Entry(form, width=30)
        self.kapasitas_entry.grid(row=4, column=1, padx=5)

        btn = tb.Frame(self)
        btn.pack(pady=10)

        tb.Button(btn, text="Tambah", bootstyle=SUCCESS, command=self.insert)\
            .pack(side=LEFT, padx=5)
        tb.Button(btn, text="Update", bootstyle=WARNING, command=self.update)\
            .pack(side=LEFT, padx=5)
        tb.Button(btn, text="Hapus", bootstyle=DANGER, command=self.delete)\
            .pack(side=LEFT, padx=5)
        tb.Button(btn, text="Reset", bootstyle=SECONDARY, command=self.reset)\
            .pack(side=LEFT, padx=5)

        self.tree = ttk.Treeview(
            self,
            columns=("nama", "trainer", "tanggal", "jam", "kapasitas"),
            show="headings"
        )
        self.tree.heading("nama", text="Nama Kelas")
        self.tree.heading("trainer", text="Trainer")
        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("jam", text="Jam")
        self.tree.heading("kapasitas", text="Kapasitas")

        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ================= LOAD =================
    def load_trainers(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nama FROM trainers")

        self.trainer_map = {}
        values = []

        for t in cur.fetchall():
            self.trainer_map[t["nama"]] = t["id"]
            values.append(t["nama"])

        self.trainer_combo["values"] = values
        conn.close()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT k.id, k.nama_kelas, t.nama AS trainer,
                   k.tanggal_kelas, k.jam_kelas, k.kapasitas
            FROM kelas k
            JOIN trainers t ON k.trainer_id = t.id
            ORDER BY k.tanggal_kelas, k.jam_kelas
        """)

        for r in cur.fetchall():
            self.tree.insert(
                "",
                END,
                iid=r["id"],
                values=(
                    r["nama_kelas"],
                    r["trainer"],
                    r["tanggal_kelas"],
                    r["jam_kelas"],
                    r["kapasitas"]
                )
            )
        conn.close()

    # ================= CRUD =================
    def insert(self):
        nama = self.nama_entry.get().strip()
        trainer_name = self.trainer_combo.get()
        tanggal = self.tanggal_entry.entry.get()
        jam = self.jam_entry.get().strip()
        kapasitas = self.kapasitas_entry.get().strip()

        if not nama or not trainer_name or not tanggal or not jam or not kapasitas:
            messagebox.showwarning("Validasi", "Semua field wajib diisi")
            return

        try:
            kapasitas = int(kapasitas)
        except ValueError:
            messagebox.showwarning("Validasi", "Kapasitas harus angka")
            return

        trainer_id = self.trainer_map.get(trainer_name)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO kelas
            (id, nama_kelas, trainer_id, tanggal_kelas, jam_kelas, kapasitas)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            nama,
            trainer_id,
            tanggal,
            jam,
            kapasitas
        ))
        conn.commit()
        conn.close()

        self.load_data()
        self.reset()

    def update(self):
        if not self.selected_id:
            messagebox.showwarning("Pilih Data", "Pilih kelas terlebih dahulu")
            return

        try:
            kapasitas = int(self.kapasitas_entry.get())
        except ValueError:
            messagebox.showwarning("Validasi", "Kapasitas harus angka")
            return

        trainer_id = self.trainer_map.get(self.trainer_combo.get())

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE kelas
            SET nama_kelas = ?, trainer_id = ?, tanggal_kelas = ?,
                jam_kelas = ?, kapasitas = ?
            WHERE id = ?
        """, (
            self.nama_entry.get(),
            trainer_id,
            self.tanggal_entry.entry.get(),
            self.jam_entry.get(),
            kapasitas,
            self.selected_id
        ))
        conn.commit()
        conn.close()

        self.load_data()
        self.reset()

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("Pilih Data", "Pilih kelas terlebih dahulu")
            return

        if not messagebox.askyesno("Konfirmasi", "Hapus kelas ini?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM kelas WHERE id = ?", (self.selected_id,))
        conn.commit()
        conn.close()

        self.load_data()
        self.reset()

    # ================= EVENT =================
    def on_select(self, _):
        sel = self.tree.selection()
        if sel:
            self.selected_id = sel[0]
            nama, trainer, tanggal, jam, kapasitas = self.tree.item(self.selected_id, "values")

            self.nama_entry.delete(0, END)
            self.nama_entry.insert(0, nama)

            self.trainer_combo.set(trainer)
            self.tanggal_entry.entry.delete(0, END)
            self.tanggal_entry.entry.insert(0, tanggal)

            self.jam_entry.delete(0, END)
            self.jam_entry.insert(0, jam)

            self.kapasitas_entry.delete(0, END)
            self.kapasitas_entry.insert(0, kapasitas)

    def reset(self):
        self.selected_id = None
        self.nama_entry.delete(0, END)
        self.trainer_combo.set("")
        self.jam_entry.delete(0, END)
        self.kapasitas_entry.delete(0, END)
