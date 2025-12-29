import sqlite3
import uuid
from datetime import date, datetime, timedelta
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
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
        # HEADER
        header_frame = tb.Frame(self)
        header_frame.pack(fill=X, padx=20, pady=20)
        tb.Label(
            header_frame,
            text="Master Data Kelas Gym",
            font=("Helvetica", 18, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)

        # FORM
        form_frame = tb.Labelframe(
            self, text="Jadwal Kelas", padding=20, bootstyle="primary"
        )
        form_frame.pack(fill=X, padx=20, pady=5)

        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        # Row 0
        tb.Label(form_frame, text="Nama Kelas:").grid(row=0, column=0, sticky=W, padx=10, pady=10)
        self.nama_entry = tb.Entry(form_frame)
        self.nama_entry.grid(row=0, column=1, sticky=EW, padx=10)

        tb.Label(form_frame, text="Trainer:").grid(row=0, column=2, sticky=W, padx=10, pady=10)
        self.trainer_combo = tb.Combobox(form_frame, state="readonly")
        self.trainer_combo.grid(row=0, column=3, sticky=EW, padx=10)

        # Row 1 – Hari
        tb.Label(form_frame, text="Hari:").grid(row=1, column=0, sticky=W, padx=10, pady=10)
        self.hari_combo = tb.Combobox(
            form_frame,
            values=["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"],
            state="readonly"
        )
        self.hari_combo.grid(row=1, column=1, sticky=EW, padx=10)

        tb.Label(form_frame, text="Jam (HH:MM):").grid(row=1, column=2, sticky=W, padx=10, pady=10)
        self.jam_entry = tb.Entry(form_frame)
        self.jam_entry.grid(row=1, column=3, sticky=EW, padx=10)

        # Row 2
        tb.Label(form_frame, text="Kapasitas (Org):").grid(row=2, column=0, sticky=W, padx=10, pady=10)
        self.kapasitas_entry = tb.Entry(form_frame)
        self.kapasitas_entry.grid(row=2, column=1, sticky=EW, padx=10)

        # BUTTONS
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill=X, padx=20, pady=20)

        tb.Button(btn_frame, text="Simpan", bootstyle=SUCCESS, command=self.insert).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Update", bootstyle=WARNING, command=self.update).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Hapus", bootstyle=DANGER, command=self.delete).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Reset", bootstyle="outline-secondary", command=self.reset).pack(side=RIGHT, padx=5)

        # TABLE
        tree_frame = tb.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))

        y_scroll = tb.Scrollbar(tree_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("nama", "trainer", "tanggal", "jam", "kapasitas"),
            show="headings",
            yscrollcommand=y_scroll.set
        )
        y_scroll.config(command=self.tree.yview)

        self.tree.heading("nama", text="Nama Kelas")
        self.tree.heading("trainer", text="Trainer")
        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("jam", text="Jam")
        self.tree.heading("kapasitas", text="Kapasitas")

        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ================= HELPER =================
    def get_next_date_from_day(self, day_name):
        days = {
            "Senin": 0, "Selasa": 1, "Rabu": 2,
            "Kamis": 3, "Jumat": 4, "Sabtu": 5, "Minggu": 6
        }

        today = date.today()
        today_idx = today.weekday()
        target_idx = days[day_name]

        delta = target_idx - today_idx
        if delta <= 0:
            delta += 7   # PAKSA minggu depan

        return today + timedelta(days=delta)
    

    def parse_tanggal(tanggal_str):
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%y",
            "%m/%d/%Y"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(tanggal_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Format tanggal tidak dikenali: {tanggal_str}")


    # ================= LOAD =================
    def load_trainers(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nama FROM trainers")

        self.trainer_map = {}
        names = []

        for t in cur.fetchall():
            self.trainer_map[t["nama"]] = t["id"]
            names.append(t["nama"])

        self.trainer_combo["values"] = names
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
        trainer = self.trainer_combo.get()
        hari = self.hari_combo.get()
        jam = self.jam_entry.get().strip()
        kapasitas = self.kapasitas_entry.get().strip()

        if not nama or not trainer or not hari or not jam or not kapasitas:
            messagebox.showwarning("Validasi", "Semua field wajib diisi")
            return

        try:
            kapasitas = int(kapasitas)
            if kapasitas <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validasi", "Kapasitas harus lebih dari 0")
            return

        try:
            jam_time = datetime.strptime(jam, "%H:%M").time()
        except ValueError:
            messagebox.showwarning("Validasi", "Format jam harus HH:MM")
            return

        tanggal = self.get_next_date_from_day(hari)
        if tanggal == date.today() and jam_time <= datetime.now().time():
            messagebox.showwarning("Validasi", "Jam kelas sudah terlewat")
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM kelas WHERE nama_kelas = ?", (nama,))
        if cur.fetchone():
            conn.close()
            messagebox.showerror("Ditolak", "Nama kelas sudah digunakan")
            return

        cur.execute("""
            INSERT INTO kelas
            (id, nama_kelas, trainer_id, tanggal_kelas, jam_kelas, kapasitas)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            nama,
            self.trainer_map[trainer],
            tanggal.isoformat(),
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

        nama = self.nama_entry.get().strip()
        trainer = self.trainer_combo.get()
        hari = self.hari_combo.get()
        jam = self.jam_entry.get().strip()

        try:
            kapasitas = int(self.kapasitas_entry.get())
            if kapasitas <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validasi", "Kapasitas harus lebih dari 0")
            return

        try:
            jam_time = datetime.strptime(jam, "%H:%M").time()
        except ValueError:
            messagebox.showwarning("Validasi", "Format jam harus HH:MM")
            return

        tanggal = self.get_next_date_from_day(hari)
        if tanggal == date.today() and jam_time <= datetime.now().time():
            messagebox.showwarning("Validasi", "Jam kelas sudah terlewat")
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 1 FROM kelas
            WHERE nama_kelas = ? AND id != ?
        """, (nama, self.selected_id))

        if cur.fetchone():
            conn.close()
            messagebox.showerror("Ditolak", "Nama kelas sudah digunakan")
            return

        cur.execute("""
            UPDATE kelas
            SET nama_kelas = ?, trainer_id = ?, tanggal_kelas = ?,
                jam_kelas = ?, kapasitas = ?
            WHERE id = ?
        """, (
            nama,
            self.trainer_map[trainer],
            tanggal.isoformat(),
            jam,
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

        conn = get_connection()
        cur = conn.cursor()

        # 1️⃣ Cek relasi ke member_kelas
        cur.execute("""
            SELECT 1 FROM member_kelas
            WHERE kelas_id = ?
            LIMIT 1
        """, (self.selected_id,))
        if cur.fetchone():
            conn.close()
            messagebox.showerror(
                "Ditolak",
                "Kelas tidak dapat dihapus karena sudah diambil oleh member"
            )
            return

        # 2️⃣ Cek relasi ke transaksi_kelas
        cur.execute("""
            SELECT 1 FROM transaksi_kelas
            WHERE kelas_id = ?
            LIMIT 1
        """, (self.selected_id,))
        if cur.fetchone():
            conn.close()
            messagebox.showerror(
                "Ditolak",
                "Kelas tidak dapat dihapus karena memiliki transaksi"
            )
            return

        # 3️⃣ Konfirmasi user
        if not messagebox.askyesno("Konfirmasi", "Hapus kelas ini?"):
            conn.close()
            return

        # 4️⃣ Hapus aman
        cur.execute("DELETE FROM kelas WHERE id = ?", (self.selected_id,))
        conn.commit()
        conn.close()

        self.load_data()
        self.reset()




    # ================= EVENT =================
    def on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return

        self.selected_id = sel[0]
        nama, trainer, tanggal, jam, kapasitas = self.tree.item(self.selected_id, "values")

        self.nama_entry.delete(0, END)
        self.nama_entry.insert(0, nama)

        self.trainer_combo.set(trainer)

        tanggal_date = MasterKelas.parse_tanggal(tanggal)

        hari_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        self.hari_combo.set(hari_list[tanggal_date.weekday()])

        self.jam_entry.delete(0, END)
        self.jam_entry.insert(0, jam)

        self.kapasitas_entry.delete(0, END)
        self.kapasitas_entry.insert(0, kapasitas)

    def reset(self):
        self.selected_id = None
        self.nama_entry.delete(0, END)
        self.trainer_combo.set("")
        self.hari_combo.set("")
        self.jam_entry.delete(0, END)
        self.kapasitas_entry.delete(0, END)
