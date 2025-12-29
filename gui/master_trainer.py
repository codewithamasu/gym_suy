import uuid
import re
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
        # HEADER
        header_frame = tb.Frame(self)
        header_frame.pack(fill=X, padx=20, pady=20)
        tb.Label(
            header_frame,
            text="Master Data Trainer",
            font=("Helvetica", 18, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)

        # FORM
        form_frame = tb.Labelframe(
            self, text="Form Input Trainer", padding=20, bootstyle="info"
        )
        form_frame.pack(fill=X, padx=20, pady=5)

        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        # Row 0
        tb.Label(form_frame, text="Nama Trainer:").grid(row=0, column=0, sticky=W, padx=10, pady=10)
        self.nama_entry = tb.Entry(form_frame)
        self.nama_entry.grid(row=0, column=1, sticky=EW, padx=10)

        tb.Label(form_frame, text="Spesialisasi:").grid(row=0, column=2, sticky=W, padx=10, pady=10)
        self.spesialisasi_combo = tb.Combobox(
            form_frame,
            values=["Strength", "Cardio", "Yoga", "Rehabilitation"],
            state="readonly"
        )
        self.spesialisasi_combo.grid(row=0, column=3, sticky=EW, padx=10)
        self.spesialisasi_combo.set("Strength")

        # Row 1
        tb.Label(form_frame, text="No. Telepon:").grid(row=1, column=0, sticky=W, padx=10, pady=10)
        self.telp_entry = tb.Entry(form_frame)
        self.telp_entry.grid(row=1, column=1, sticky=EW, padx=10)

        tb.Label(form_frame, text="Tarif / Sesi (Rp):").grid(row=1, column=2, sticky=W, padx=10, pady=10)
        self.tarif_entry = tb.Entry(form_frame)
        self.tarif_entry.grid(row=1, column=3, sticky=EW, padx=10)

        # BUTTONS
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill=X, padx=20, pady=20)

        tb.Button(btn_frame, text="Simpan", bootstyle=SUCCESS, command=self.insert).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Update", bootstyle=WARNING, command=self.update).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Hapus", bootstyle=DANGER, command=self.delete).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Reset", bootstyle="outline-secondary", command=self.reset_form).pack(side=RIGHT, padx=5)

        # TABLE
        tree_frame = tb.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))

        y_scroll = tb.Scrollbar(tree_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("nama", "spesialisasi", "telp", "tarif"),
            show="headings",
            yscrollcommand=y_scroll.set
        )
        y_scroll.config(command=self.tree.yview)

        self.tree.heading("nama", text="Nama Trainer")
        self.tree.heading("spesialisasi", text="Spesialisasi")
        self.tree.heading("telp", text="No. Telepon")
        self.tree.heading("tarif", text="Tarif / Sesi")

        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ================= DATABASE =================
    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM trainers")
        for r in cur.fetchall():
            self.tree.insert(
                "",
                END,
                iid=r["id"],
                values=(r["nama"], r["spesialisasi"], r["no_telepon"], r["tarif_per_sesi"])
            )
        conn.close()

    # ================= CRUD =================
    def insert(self):
        nama = self.nama_entry.get().strip()
        spesialisasi = self.spesialisasi_combo.get()
        telp = self.telp_entry.get().strip()
        tarif = self.tarif_entry.get().strip()

        # ===== Validasi kosong =====
        if not nama or not telp or not tarif:
            messagebox.showwarning("Validasi", "Semua field wajib diisi")
            return

        # ===== Nama tidak boleh angka =====
        if any(c.isdigit() for c in nama):
            messagebox.showwarning("Validasi", "Nama tidak boleh mengandung angka")
            return

        # ===== Validasi no telp Indonesia =====
        if not re.match(r"^\+62[0-9]{9,13}$", telp):
            messagebox.showwarning("Validasi", "No. Telepon harus diawali +62")
            return

        # ===== Tarif =====
        try:
            tarif = int(tarif)
            if tarif <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validasi", "Tarif harus angka dan lebih dari 0")
            return

        conn = get_connection()
        cur = conn.cursor()

        # ===== Cek duplikasi nama atau telp =====
        cur.execute("""
            SELECT 1 FROM trainers
            WHERE nama = ? OR no_telepon = ?
        """, (nama, telp))

        if cur.fetchone():
            conn.close()
            messagebox.showerror(
                "Ditolak",
                "Nama atau No. Telepon sudah terdaftar"
            )
            return

        cur.execute("""
            INSERT INTO trainers (id, nama, spesialisasi, no_telepon, tarif_per_sesi)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            nama,
            spesialisasi,
            telp,
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

        nama = self.nama_entry.get().strip()
        telp = self.telp_entry.get().strip()

        if any(c.isdigit() for c in nama):
            messagebox.showwarning("Validasi", "Nama tidak boleh mengandung angka")
            return

        try:
            tarif = int(self.tarif_entry.get())
            if tarif <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validasi", "Tarif harus angka dan lebih dari 0")
            return

        conn = get_connection()
        cur = conn.cursor()

        # Duplikasi (kecuali dirinya sendiri)
        cur.execute("""
            SELECT 1 FROM trainers
            WHERE (nama = ? OR no_telepon = ?) AND id != ?
        """, (nama, telp, self.selected_id))

        if cur.fetchone():
            conn.close()
            messagebox.showerror("Ditolak", "Nama atau No. Telepon sudah digunakan")
            return

        cur.execute("""
            UPDATE trainers
            SET nama = ?, spesialisasi = ?, no_telepon = ?, tarif_per_sesi = ?
            WHERE id = ?
        """, (
            nama,
            self.spesialisasi_combo.get(),
            telp,
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

        conn = get_connection()
        cur = conn.cursor()

        # CEK RELASI KE KELAS
        cur.execute("""
            SELECT 1 FROM kelas
            WHERE trainer_id = ?
            LIMIT 1
        """, (self.selected_id,))

        if cur.fetchone():
            conn.close()
            messagebox.showerror(
                "Ditolak",
                "Trainer tidak dapat dihapus karena masih digunakan pada jadwal kelas"
            )
            return

        if not messagebox.askyesno("Konfirmasi", "Hapus trainer ini?"):
            conn.close()
            return

        cur.execute("DELETE FROM trainers WHERE id = ?", (self.selected_id,))
        conn.commit()
        conn.close()

        self.load_data()
        self.reset_form()


    # ================= EVENT =================
    def on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return

        self.selected_id = sel[0]
        nama, spesialisasi, telp, tarif = self.tree.item(self.selected_id, "values")

        self.nama_entry.delete(0, END)
        self.nama_entry.insert(0, nama)

        self.spesialisasi_combo.set(spesialisasi)

        self.telp_entry.delete(0, END)
        self.telp_entry.insert(0, telp)

        self.tarif_entry.delete(0, END)
        self.tarif_entry.insert(0, tarif)

    def reset_form(self):
        self.selected_id = None
        self.nama_entry.delete(0, END)
        self.spesialisasi_combo.set("Strength")
        self.telp_entry.delete(0, END)
        self.tarif_entry.delete(0, END)
