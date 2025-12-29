import uuid
from datetime import datetime
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from database.db import get_connection
from models.transaksi_kelas import TransaksiKelas
from models.pembayaran import Pembayaran


class TransaksiKelas(tb.Frame):
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
            text="Transaksi Kelas",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        self.tree = ttk.Treeview(
            self,
            columns=("member", "kelas", "trainer", "tarif", "status"),
            show="headings"
        )

        self.tree.heading("member", text="Member")
        self.tree.heading("kelas", text="Kelas")
        self.tree.heading("trainer", text="Trainer")
        self.tree.heading("tarif", text="Tarif")
        self.tree.heading("status", text="Status")

        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        btn = tb.Frame(self)
        btn.pack(pady=10)

        tb.Button(btn, text="Bayar", bootstyle=PRIMARY, command=self.open_struk)\
            .pack(side=LEFT, padx=5)

    # ================= LOAD =================
    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT tk.id,
                   m.nama AS member,
                   k.nama_kelas AS kelas,
                   t.nama AS trainer,
                   t.tarif_per_sesi AS tarif,
                   CASE
                     WHEN pb.id IS NULL THEN 'BELUM BAYAR'
                     ELSE 'LUNAS'
                   END AS status
            FROM transaksi_kelas tk
            JOIN members m ON tk.member_id = m.id
            JOIN kelas k ON tk.kelas_id = k.id
            JOIN trainers t ON k.trainer_id = t.id
            LEFT JOIN pembayaran pb
              ON pb.transaksi_id = tk.id
             AND pb.jenis_transaksi = 'KELAS'
            ORDER BY tk.tanggal_daftar DESC
        """)

        for r in cur.fetchall():
            self.tree.insert(
                "",
                END,
                iid=r["id"],
                values=(
                    r["member"],
                    r["kelas"],
                    r["trainer"],
                    f"Rp{r['tarif']:,}".replace(",", "."),
                    r["status"]
                )
            )

        conn.close()

    # ================= EVENT =================
    def on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            self.selected = None
            return

        iid = sel[0]
        values = self.tree.item(iid, "values")

        self.selected = {
            "id": iid,
            "member": values[0],
            "kelas": values[1],
            "trainer": values[2],
            "tarif": int(values[3].replace("Rp", "").replace(".", "")),
            "status": values[4]
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
        win.title("Struk Pembayaran Kelas")
        win.geometry("400x350")
        win.transient(self)
        win.grab_set()

        tb.Label(win, text="STRUK PEMBAYARAN", font=("Segoe UI", 14, "bold")).pack(pady=10)

        transaksi = TransaksiKelas(
            transaksi_id=self.selected["id"],
            member_id=None,
            tarif=self.selected["tarif"]
        )

        pembayaran = Pembayaran(transaksi)

        info = tb.Frame(win)
        info.pack(padx=10, pady=10, fill=X)

        def row(label, value):
            f = tb.Frame(info)
            f.pack(fill=X, pady=2)
            tb.Label(f, text=label, width=15, anchor=W).pack(side=LEFT)
            tb.Label(f, text=value, anchor=W).pack(side=LEFT)

        row("Member", self.selected["member"])
        row("Kelas", self.selected["kelas"])
        row("Trainer", self.selected["trainer"])
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
            f"Pembayaran kelas berhasil\nKembalian: Rp{kembalian:,}".replace(",", ".")
        )

        win.destroy()
        self.load_data()
