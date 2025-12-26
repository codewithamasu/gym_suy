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
        # HEADER
        header_frame = tb.Frame(self)
        header_frame.pack(fill=X, padx=20, pady=20)
        tb.Label(
            header_frame,
            text="Master Paket Membership",
            font=("Helvetica", 18, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)

        # FORM CONTAINER
        form_frame = tb.Labelframe(self, text="Form Paket", padding=20, bootstyle="primary")
        form_frame.pack(fill=X, padx=20, pady=5)
        
        form_frame.columnconfigure(1, weight=1)

        # Row 0: Durasi
        tb.Label(form_frame, text="Durasi (Bulan):").grid(row=0, column=0, sticky=W, padx=10, pady=10)
        self.durasi_combo = tb.Combobox(
            form_frame,
            values=[1, 2, 3, 6, 12],
            state="readonly"
        )
        self.durasi_combo.grid(row=0, column=1, sticky=EW, padx=10)
        self.durasi_combo.set(1)
        self.durasi_combo.bind("<<ComboboxSelected>>", self.update_harga)

        # Row 1: Harga
        tb.Label(form_frame, text="Harga (Rp):").grid(row=1, column=0, sticky=W, padx=10, pady=10)
        
        # Frame for cost + auto calc info
        harga_frame = tb.Frame(form_frame)
        harga_frame.grid(row=1, column=1, sticky=EW, padx=10)
        
        self.harga_entry = tb.Entry(harga_frame)
        self.harga_entry.pack(side=LEFT, fill=X, expand=True)
        tb.Label(harga_frame, text="*Auto-calculated based on duration", font=("Helvetica", 8, "italic"), bootstyle="secondary").pack(side=LEFT, padx=10)

        self.update_harga()

        # BUTTONS
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill=X, padx=20, pady=20)
        
        tb.Button(btn_frame, text="Simpan", bootstyle="success", command=self.insert).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Update", bootstyle="warning", command=self.update).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Hapus", bootstyle="danger", command=self.delete).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Reset", bootstyle="outline-secondary", command=self.reset).pack(side=RIGHT, padx=5)

        # TABLE
        tree_frame = tb.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        y_scroll = tb.Scrollbar(tree_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("durasi", "harga"),
            show="headings",
            yscrollcommand=y_scroll.set,
            style="primary.Treeview"
        )
        y_scroll.config(command=self.tree.yview)

        self.tree.heading("durasi", text="Durasi (Bulan)")
        self.tree.heading("harga", text="Harga (Rp)")
        
        self.tree.pack(fill=BOTH, expand=True)
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
