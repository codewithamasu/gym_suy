import uuid
from datetime import datetime
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection


HARGA_HARIAN = 20000


class TransaksiHarian(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)

        self.create_widgets()
        self.load_data()

    # ================= UI =================
    def create_widgets(self):
        # HEADER
        header_frame = tb.Frame(self)
        header_frame.pack(fill=X, padx=20, pady=20)
        tb.Label(
            header_frame,
            text="Transaksi Harian (Non-Member)",
            font=("Helvetica", 18, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)

        # FORM CONTAINER
        form_frame = tb.Labelframe(self, text="Registrasi Pengunjung", padding=20, bootstyle="primary")
        form_frame.pack(fill=X, padx=20, pady=5)
        
        form_frame.columnconfigure(1, weight=1)

        # Row 0: Nama
        tb.Label(form_frame, text="Nama Pengunjung:").grid(row=0, column=0, sticky=W, padx=10, pady=10)
        self.nama_entry = tb.Entry(form_frame)
        self.nama_entry.grid(row=0, column=1, sticky=EW, padx=10)

        # Row 1: Harga
        tb.Label(form_frame, text="Harga Tiket (Rp):").grid(row=1, column=0, sticky=W, padx=10, pady=10)
        self.harga_entry = tb.Entry(form_frame, state="readonly")
        self.harga_entry.grid(row=1, column=1, sticky=EW, padx=10)
        self.set_harga()

        # BUTTONS
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill=X, padx=20, pady=20)
        
        tb.Button(
            btn_frame, text="Simpan Transaksi", bootstyle="success", command=self.insert
        ).pack(side=LEFT, padx=5)

        tb.Button(
            btn_frame, text="Export CSV", bootstyle="info", command=self.export_csv
        ).pack(side=RIGHT, padx=5)

        # TABLE
        tree_frame = tb.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        y_scroll = tb.Scrollbar(tree_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("nama", "tanggal", "jam", "harga"),
            show="headings",
            yscrollcommand=y_scroll.set,
            style="primary.Treeview"
        )
        y_scroll.config(command=self.tree.yview)

        self.tree.heading("nama", text="Nama")
        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("jam", text="Jam Masuk")
        self.tree.heading("harga", text="Harga")
        
        self.tree.column("nama", width=200)
        self.tree.column("harga", width=100)

        self.tree.pack(fill=BOTH, expand=True)

    # ================= LOGIC =================
    def set_harga(self):
        self.harga_entry.config(state="normal")
        self.harga_entry.delete(0, END)
        self.harga_entry.insert(0, HARGA_HARIAN)
        self.harga_entry.config(state="readonly")

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT nama_pengunjung, tanggal, waktu_masuk, harga
            FROM transaksi_harian
            ORDER BY tanggal DESC, waktu_masuk DESC
        """)

        for r in cur.fetchall():
            self.tree.insert(
                "",
                END,
                values=(r["nama_pengunjung"], r["tanggal"], r["waktu_masuk"], r["harga"])
            )

        conn.close()

    def insert(self):
        nama = self.nama_entry.get().strip()
        if not nama:
            messagebox.showwarning("Validasi", "Nama pengunjung wajib diisi")
            return

        now = datetime.now()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO transaksi_harian
            (id, nama_pengunjung, tanggal, harga, waktu_masuk)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            nama,
            now.date().isoformat(),
            HARGA_HARIAN,
            now.strftime("%H:%M:%S")
        ))

        conn.commit()
        conn.close()

        self.nama_entry.delete(0, END)
        self.load_data()
        messagebox.showinfo("Sukses", "Transaksi harian berhasil disimpan")

    # ================= EXPORT =================
    def export_csv(self):
        try:
            import pandas as pd
            from tkinter import filedialog
            
            conn = get_connection()
            query = """
                SELECT nama_pengunjung, tanggal, waktu_masuk, harga
                FROM transaksi_harian
                ORDER BY tanggal DESC
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                messagebox.showinfo("Info", "Tidak ada data untuk diexport.")
                return

            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="Simpan Laporan Transaksi Harian"
            )
            
            if filename:
                df.to_csv(filename, index=False)
                messagebox.showinfo("Sukses", f"Data berhasil diexport ke:\n{filename}")
                
        except ImportError:
            messagebox.showerror("Error", "Modul 'pandas' belum terinstall.")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export data: {str(e)}")
