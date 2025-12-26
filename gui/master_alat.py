import uuid
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection

class MasterAlat(tb.Frame):
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
            text="Master Data Alat Gym",
            font=("Helvetica", 18, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)

        # FORM CONTAINER
        form_frame = tb.Labelframe(self, text="Form Input Alat", padding=20, bootstyle="primary")
        form_frame.pack(fill=X, padx=20, pady=5)
        
        form_frame.columnconfigure(1, weight=1)

        # Row 0: Nama Alat
        tb.Label(form_frame, text="Nama Alat:").grid(row=0, column=0, sticky=W, padx=10, pady=10)
        self.nama_entry = tb.Entry(form_frame)
        self.nama_entry.grid(row=0, column=1, sticky=EW, padx=10)

        # Row 1: Kondisi
        tb.Label(form_frame, text="Kondisi:").grid(row=1, column=0, sticky=W, padx=10, pady=10)
        self.kondisi_combo = tb.Combobox(
            form_frame,
            values=["Bagus", "Rusak Ringan", "Rusak Berat", "Perlu Maintenance"],
            state="readonly"
        )
        self.kondisi_combo.grid(row=1, column=1, sticky=EW, padx=10)
        self.kondisi_combo.set("Bagus")

        # BUTTONS
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill=X, padx=20, pady=20)
        
        tb.Button(btn_frame, text="Simpan", bootstyle="success", command=self.insert).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Update", bootstyle="warning", command=self.update).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Hapus", bootstyle="danger", command=self.delete).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Reset", bootstyle="outline-secondary", command=self.reset_form).pack(side=RIGHT, padx=5)

        # TABLE
        tree_frame = tb.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        y_scroll = tb.Scrollbar(tree_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("nama", "kondisi"),
            show="headings",
            yscrollcommand=y_scroll.set,
            style="primary.Treeview"
        )
        y_scroll.config(command=self.tree.yview)

        self.tree.heading("nama", text="Nama Alat")
        self.tree.heading("kondisi", text="Kondisi")
        
        self.tree.column("nama", width=300)
        self.tree.column("kondisi", width=150)

        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ================= DATABASE =================
    def load_data(self):
        self.tree.delete(*self.tree.get_children())

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alat_gym")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert(
                "",
                END,
                iid=row["id"],
                values=(row["nama_alat"], row["kondisi"])
            )

    def insert(self):
        nama = self.nama_entry.get().strip()
        kondisi = self.kondisi_combo.get()

        if not nama:
            messagebox.showwarning("Validasi", "Nama alat wajib diisi")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO alat_gym (id, nama_alat, kondisi)
                VALUES (?, ?, ?)
            """, (
                str(uuid.uuid4()),
                nama,
                kondisi
            ))
            conn.commit()
            messagebox.showinfo("Sukses", "Data alat berhasil disimpan")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

        self.load_data()
        self.reset_form()

    def update(self):
        if not self.selected_id:
            messagebox.showwarning("Pilih Data", "Pilih alat terlebih dahulu")
            return
        
        nama = self.nama_entry.get().strip()
        kondisi = self.kondisi_combo.get()

        if not nama:
            messagebox.showwarning("Validasi", "Nama alat tidak boleh kosong")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE alat_gym
                SET nama_alat = ?, kondisi = ?
                WHERE id = ?
            """, (
                nama,
                kondisi,
                self.selected_id
            ))
            conn.commit()
            messagebox.showinfo("Sukses", "Data alat berhasil diperbarui")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

        self.load_data()
        self.reset_form()

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("Pilih Data", "Pilih alat terlebih dahulu")
            return

        if not messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus alat ini?"):
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM alat_gym WHERE id = ?", (self.selected_id,))
            conn.commit()
            messagebox.showinfo("Sukses", "Data alat berhasil dihapus")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
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

        self.kondisi_combo.set(values[1])

    def reset_form(self):
        self.selected_id = None
        self.nama_entry.delete(0, END)
        self.kondisi_combo.set("Bagus")
