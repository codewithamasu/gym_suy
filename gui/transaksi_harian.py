import uuid
from datetime import datetime
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from database.db import get_connection
from models.transaksi_harian import TransaksiHarian as TransaksiHarianModel
from models.pembayaran import Pembayaran


class TransaksiHarianView(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)

        self.selected = None
        self.create_widgets()
        self.load_data()

    # ================= UI =================
    def create_widgets(self):
        tb.Label(
            self,
            text="Transaksi Harian (Non Membership)",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        # ===== FORM =====
        form = tb.Frame(self)
        form.pack(pady=10)

        tb.Label(form, text="Nama Pengunjung").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.nama_entry = tb.Entry(form, width=30)
        self.nama_entry.grid(row=0, column=1, padx=5, pady=5)


        tb.Button(
            form,
            text="Tambah Transaksi",
            bootstyle=SUCCESS,
            command=self.insert
        ).grid(row=2, column=1, sticky=W, padx=5, pady=10)

        # ===== TABLE =====
        self.tree = ttk.Treeview(
            self,
            columns=("nama", "hari", "total", "status"),
            show="headings"
        )

        self.tree.heading("nama", text="Nama")
        self.tree.heading("hari", text="Hari")
        self.tree.heading("total", text="Total")
        self.tree.heading("status", text="Status")

        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ===== BUTTON =====
        btn = tb.Frame(self)
        btn.pack(pady=10)

        tb.Button(
            btn, text="Bayar", bootstyle=PRIMARY, command=self.open_struk
        ).pack(side=LEFT, padx=5)

        tb.Button(
            btn, text="Hapus", bootstyle=DANGER, command=self.delete
        ).pack(side=LEFT, padx=5)

    # ================= LOAD =================
    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT th.id, th.nama_pengunjung, th.tanggal, th.harga,
                CASE
                    WHEN pb.id IS NULL THEN 'BELUM BAYAR'
                    ELSE 'LUNAS'
                END AS status
            FROM transaksi_harian th
            LEFT JOIN pembayaran pb
            ON pb.transaksi_id = th.id
            AND pb.jenis_transaksi = 'HARIAN'
            ORDER BY th.tanggal DESC
        """)

        for r in cur.fetchall():
            self.tree.insert(
                "",
                END,
                iid=r["id"],
                values=(
                    r["nama_pengunjung"],
                    r["tanggal"],
                    f"Rp{r['harga']:,}".replace(",", "."),
                    r["status"]
                )
            )

        conn.close()


    # ================= CRUD =================
    def insert(self):
        nama = self.nama_entry.get().strip()

        if not nama:
            messagebox.showwarning("Validasi", "Nama pengunjung wajib diisi")
            return
        if nama.isdigit() or any(char.isdigit() for char in nama):
            messagebox.showwarning("Validasi", "Nama pengunjung tidak boleh angka")
            return

        today = datetime.now().date().isoformat()

        # ===== VALIDASI DUPLIKAT =====
        if self.is_transaksi_harian_exists(nama, today):
            messagebox.showwarning(
                "Validasi",
                "Pengunjung ini sudah terdaftar hari ini"
            )
            return

        conn = get_connection()
        cur = conn.cursor()

        now = datetime.now()

        cur.execute("""
            INSERT INTO transaksi_harian
            (id, nama_pengunjung, tanggal, harga, waktu_masuk)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            nama,
            today,
            20000,
            now.time().strftime("%H:%M:%S")
        ))

        conn.commit()
        conn.close()

        self.nama_entry.delete(0, END)
        self.load_data()

    def delete(self):
        if not self.selected:
            messagebox.showwarning("Pilih Data", "Pilih transaksi terlebih dahulu")
            return

        if not messagebox.askyesno("Konfirmasi", "Hapus transaksi ini?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM transaksi_harian WHERE id = ?", (self.selected["id"],))
        conn.commit()
        conn.close()

        self.selected = None
        self.load_data()

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            self.selected = None
            return

        iid = sel[0]
        nama, tanggal, harga, status = self.tree.item(iid, "values")

        self.selected = {
            "id": iid,
            "nama": nama,
            "tanggal": tanggal,
            "harga": int(
                harga.replace("Rp", "").replace(".", "")
            ),
            "status": status
        }


    # ================= STRUK =================
    def open_struk(self):
        if not self.selected:
            messagebox.showwarning("Pilih Data", "Pilih transaksi terlebih dahulu")
            return

        if self.selected["status"] == "LUNAS":
            messagebox.showinfo("Info", "Transaksi ini sudah lunas")
            return

        win = tb.Toplevel(self)
        win.title("Struk Pembayaran Harian")
        win.geometry("400x350")
        win.transient(self)
        win.grab_set()

        tb.Label(win, text="STRUK PEMBAYARAN", font=("Segoe UI", 14, "bold")).pack(pady=10)

        transaksi = TransaksiHarianModel(
            transaksi_id=self.selected["id"],
            member_id=None,
            harga=self.selected["harga"]
        )

        pembayaran = Pembayaran(transaksi)


        info = tb.Frame(win)
        info.pack(padx=10, pady=10, fill=X)

        def row(label, value):
            f = tb.Frame(info)
            f.pack(fill=X, pady=2)
            tb.Label(f, text=label, width=15, anchor=W).pack(side=LEFT)
            tb.Label(f, text=value, anchor=W).pack(side=LEFT)

        row("Nama", self.selected["nama"])
        row("Harga", str(self.selected["harga"]))
        row("Total", f"Rp{pembayaran.total:,}".replace(",", "."))

        tb.Separator(win).pack(fill=X, padx=10, pady=10)

        tb.Label(win, text="Uang Diterima").pack(anchor=W, padx=10)
        uang_entry = tb.Entry(win)
        uang_entry.pack(padx=10, pady=5)

        kembalian_lbl = tb.Label(win, text="Kembalian: Rp0")
        kembalian_lbl.pack(padx=10, pady=5)

        def hitung(_=None):
            try:
                u = int(uang_entry.get())
                if u >= pembayaran.total:
                    k = u - pembayaran.total
                    kembalian_lbl.config(
                        text=f"Kembalian: Rp{k:,}".replace(",", "."),
                        foreground="green"
                    )
                else:
                    kembalian_lbl.config(text="Kembalian: Rp0", foreground="red")
            except ValueError:
                kembalian_lbl.config(text="Kembalian: Rp0", foreground="black")

        uang_entry.bind("<KeyRelease>", hitung)

        tb.Button(
            win,
            text="Bayar",
            bootstyle=SUCCESS,
            command=lambda: self.proses_bayar(win, uang_entry, transaksi, pembayaran)
        ).pack(pady=15)

    # ================= LOGIC =================
    def proses_bayar(self, win, uang_entry, transaksi, pembayaran):
        try:
            diterima = int(uang_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Uang diterima harus angka")
            return

        try:
            kembalian = pembayaran.proses(diterima)
        except ValueError as e:
            messagebox.showerror("Gagal", str(e))
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO pembayaran
            (id, transaksi_id, jenis_transaksi, total,
             uang_diterima, kembalian, tanggal_bayar)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            transaksi.transaksi_id,
            pembayaran.jenis_transaksi,
            pembayaran.total,
            diterima,
            kembalian,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Sukses",
            f"Pembayaran berhasil\nKembalian: Rp{kembalian:,}".replace(",", ".")
        )

        win.destroy()
        self.load_data()

    def is_transaksi_harian_exists(self, nama, tanggal):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 1
            FROM transaksi_harian
            WHERE LOWER(nama_pengunjung) = LOWER(?)
            AND tanggal = ?
        """, (nama, tanggal))

        exists = cur.fetchone() is not None
        conn.close()
        return exists

