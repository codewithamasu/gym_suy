import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection
from utils.auth import hash_password
import re

class MasterMember(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)

        self.selected_id = None

        self.create_widgets()
        self.load_data()

    # ================= UI =================
    # ================= UI =================
    def create_widgets(self):
        # HEADER
        header_frame = tb.Frame(self)
        header_frame.pack(fill=X, padx=20, pady=20)
        tb.Label(
            header_frame,
            text="Master Data Member",
            font=("Helvetica", 18, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)

        # FORM CONTAINER
        form_frame = tb.Labelframe(self, text="Form Input Data", padding=20, bootstyle="info")
        form_frame.pack(fill=X, padx=20, pady=5)
        
        # Grid Configuration
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        # Row 1
        tb.Label(form_frame, text="Nama Lengkap:").grid(row=0, column=0, sticky=W, padx=10, pady=10)
        self.nama_entry = tb.Entry(form_frame)
        self.nama_entry.grid(row=0, column=1, sticky=EW, padx=10)

        tb.Label(form_frame, text="Umur:").grid(row=0, column=2, sticky=W, padx=10, pady=10)
        self.umur_entry = tb.Entry(form_frame)
        self.umur_entry.grid(row=0, column=3, sticky=EW, padx=10)

        # Row 2
        tb.Label(form_frame, text="Jenis Kelamin:").grid(row=1, column=0, sticky=W, padx=10, pady=10)
        self.jk_combo = tb.Combobox(
            form_frame,
            values=["L", "P"],
            state="readonly"
        )
        self.jk_combo.grid(row=1, column=1, sticky=EW, padx=10)
        self.jk_combo.set("L")

        # BUTTON ACTION BAR
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill=X, padx=20, pady=20)
        
        # Left side buttons
        tb.Button(btn_frame, text="Simpan", bootstyle="success", command=self.insert).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Update", bootstyle="warning", command=self.update).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Hapus", bootstyle="danger", command=self.delete).pack(side=LEFT, padx=5)
        
        # Right side button
        tb.Button(btn_frame, text="Reset Form", bootstyle="outline-secondary", command=self.reset_form).pack(side=RIGHT, padx=5)

        # TABLE AREA
        tree_frame = tb.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Scrollbar
        y_scroll = tb.Scrollbar(tree_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("nama", "umur", "jk"),
            show="headings",
            yscrollcommand=y_scroll.set,
            style="info.Treeview" # Use boootstyle
        )
        y_scroll.config(command=self.tree.yview)

        self.tree.heading("nama", text="Nama Member")
        self.tree.heading("umur", text="Umur")
        self.tree.heading("jk", text="Jenis Kelamin")

        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ================= DATABASE =================
    

    @staticmethod
    def generate_member_id(conn, nama):
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM members")
        rows = cursor.fetchall()

        max_number = 0
        pattern = re.compile(r"^M-(\d+)_")

        for r in rows:
            match = pattern.match(r["id"])
            if match:
                num = int(match.group(1))
                max_number = max(max_number, num)

        safe_name = nama.lower().replace(" ", "")
        return f"M-{max_number + 1}_{safe_name}"

    
    def load_data(self):
        self.tree.delete(*self.tree.get_children())

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert(
                "",
                END,
                iid=row["id"],
                values=(row["nama"], row["umur"], row["jenis_kelamin"])
            )

    def insert(self):
        nama = self.nama_entry.get().strip()
        umur = self.umur_entry.get().strip()
        jk = self.jk_combo.get()

        if not nama or not umur or not jk:
            messagebox.showwarning("Validasi", "Semua field wajib diisi")
            return

        try:
            umur = int(umur)
        except ValueError:
            messagebox.showwarning("Validasi", "Umur harus angka")
            return

        conn = get_connection()
        cursor = conn.cursor()

        try:
            # 1️⃣ Generate member ID
            member_id = MasterMember.generate_member_id(conn, nama)

            # 2️⃣ Insert ke members
            cursor.execute("""
                INSERT INTO members (id, nama, umur, jenis_kelamin)
                VALUES (?, ?, ?, ?)
            """, (member_id, nama, umur, jk))

            # 3️⃣ Auto-create user account
            default_password = "123456"   # bisa kamu ganti
            cursor.execute("""
                INSERT INTO users (id, username, password, role)
                VALUES (?, ?, ?, 'MEMBER')
            """, (
                member_id,                 # id sama
                member_id,                 # username = member_id
                hash_password(default_password)
            ))

            conn.commit()

            messagebox.showinfo(
                "Sukses",
                f"Member berhasil dibuat\n\n"
                f"Username: {member_id}\n"
                f"Password: {default_password}"
            )

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))

        finally:
            conn.close()

        self.load_data()
        self.reset_form()


    def update(self):
        if not self.selected_id:
            messagebox.showwarning("Pilih Data", "Pilih member terlebih dahulu")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE members
            SET nama = ?, umur = ?, jenis_kelamin = ?
            WHERE id = ?
        """, (
            self.nama_entry.get(),
            self.umur_entry.get(),
            self.jk_combo.get(),
            self.selected_id
        ))
        conn.commit()
        conn.close()

        self.load_data()
        self.reset_form()

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("Pilih Data", "Pilih member terlebih dahulu")
            return

        conn = get_connection()
        cursor = conn.cursor()

        # Cek relasi
        cursor.execute("""
            SELECT 1 FROM transaksi_membership WHERE member_id = ?
            UNION
            SELECT 1 FROM absensi WHERE member_id = ?
        """, (self.selected_id, self.selected_id))

        if cursor.fetchone():
            messagebox.showerror(
                "Ditolak",
                "Member tidak bisa dihapus karena memiliki riwayat transaksi atau absensi"
            )
            conn.close()
            return

        if not messagebox.askyesno("Konfirmasi", "Hapus member ini?"):
            conn.close()
            return

        cursor.execute("DELETE FROM members WHERE id = ?", (self.selected_id,))
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

        self.umur_entry.delete(0, END)
        self.umur_entry.insert(0, values[1])

        self.jk_combo.set(values[2])

    def reset_form(self):
        self.selected_id = None
        self.nama_entry.delete(0, END)
        self.umur_entry.delete(0, END)
        self.jk_combo.set("L")

    

