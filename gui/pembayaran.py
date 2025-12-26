import uuid
from datetime import datetime
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection


class Pembayaran(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)

        self.selected = None  # simpan data baris terpilih
        self.create_widgets()
        self.load_transaksi()

    # ================= UI =================
    # ================= UI =================
    def create_widgets(self):
        # HEADER
        header_frame = tb.Frame(self)
        header_frame.pack(fill=X, padx=20, pady=20)
        tb.Label(
            header_frame,
            text="Menu Pembayaran Membership",
            font=("Helvetica", 18, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)

        # ACTION BAR
        action_frame = tb.Frame(self)
        action_frame.pack(fill=X, padx=20, pady=10)

        tb.Label(action_frame, text="Pilih Transaksi untuk dibayar:", font=("Helvetica", 11), bootstyle="secondary").pack(side=LEFT, padx=5)
        
        tb.Button(
            action_frame, 
            text="Proses Pembayaran", 
            bootstyle="success", 
            command=self.open_struk
        ).pack(side=RIGHT, padx=5)

        # TABLE
        tree_frame = tb.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        y_scroll = tb.Scrollbar(tree_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("id", "member", "durasi", "mulai", "akhir", "harga", "status"),
            show="headings",
            yscrollcommand=y_scroll.set,
            style="primary.Treeview"
        )
        y_scroll.config(command=self.tree.yview)

        self.tree.heading("id", text="ID")
        self.tree.heading("member", text="Member")
        self.tree.heading("durasi", text="Durasi (Bulan)")
        self.tree.heading("mulai", text="Mulai")
        self.tree.heading("akhir", text="Berakhir")
        self.tree.heading("harga", text="Total Tagihan")
        self.tree.heading("status", text="Status")

        self.tree.column("id", width=0, stretch=False)
        self.tree.column("member", width=150)
        self.tree.column("durasi", width=100)
        self.tree.column("status", width=100)
        
        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ================= LOAD =================
    def load_transaksi(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT tm.id,
                   m.nama,
                   p.durasi_bulan,
                   tm.tanggal_mulai,
                   tm.tanggal_berakhir,
                   p.harga,
                   CASE
                     WHEN pb.id IS NULL THEN 'BELUM BAYAR'
                     ELSE 'LUNAS'
                   END AS status
            FROM transaksi_membership tm
            JOIN members m ON tm.member_id = m.id
            JOIN paket_membership p ON tm.paket_id = p.id
            LEFT JOIN pembayaran pb
              ON pb.transaksi_id = tm.id
             AND pb.jenis_transaksi = 'MEMBERSHIP'
            ORDER BY tm.tanggal_mulai DESC
        """)

        for r in cur.fetchall():
            self.tree.insert(
                "",
                END,
                iid=r["id"],
                values=(
                    r["id"],
                    r["nama"],
                    r["durasi_bulan"],
                    r["tanggal_mulai"],
                    r["tanggal_berakhir"],
                    r["harga"],
                    r["status"]
                )
            )
        conn.close()

    # ================= EVENTS =================
    def on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            self.selected = None
            return
        vals = self.tree.item(sel[0], "values")
        self.selected = {
            "transaksi_id": vals[0],
            "member": vals[1],
            "durasi": vals[2],
            "mulai": vals[3],
            "akhir": vals[4],
            "total": int(vals[5]),
            "status": vals[6],
        }

    # ================= STRUK POPUP =================
    def open_struk(self):
        if not self.selected:
            messagebox.showwarning("Pilih Data", "Pilih transaksi terlebih dahulu")
            return

        if self.selected["status"] == "LUNAS":
            messagebox.showinfo("Info", "Transaksi ini sudah lunas")
            return

        win = tb.Toplevel(self)
        win.title("Struk Pembayaran")
        win.geometry("420x420")
        win.transient(self)
        win.grab_set()

        # ---- Header
        tb.Label(win, text="STRUK PEMBAYARAN", font=("Segoe UI", 14, "bold")).pack(pady=10)
        sep = tb.Separator(win)
        sep.pack(fill=X, padx=10, pady=5)

        # ---- Info
        info = tb.Frame(win)
        info.pack(padx=10, pady=5, fill=X)

        def row(lbl, val):
            f = tb.Frame(info)
            f.pack(fill=X, pady=2)
            tb.Label(f, text=lbl, width=15, anchor=W).pack(side=LEFT)
            tb.Label(f, text=val, anchor=W).pack(side=LEFT)

        row("Member", self.selected["member"])
        row("Durasi", f"{self.selected['durasi']} Bulan")
        row("Mulai", self.selected["mulai"])
        row("Berakhir", self.selected["akhir"])
        row("Total", f"Rp{self.selected['total']:,}".replace(",", "."))

        sep2 = tb.Separator(win)
        sep2.pack(fill=X, padx=10, pady=8)

        # ---- Input
        form = tb.Frame(win)
        form.pack(padx=10, pady=5, fill=X)

        tb.Label(form, text="Uang Diterima").grid(row=0, column=0, sticky=W, pady=5)
        uang_entry = tb.Entry(form, width=20)
        uang_entry.grid(row=0, column=1, pady=5)

        kembalian_lbl = tb.Label(form, text="Kembalian: Rp0")
        kembalian_lbl.grid(row=1, column=1, sticky=W, pady=5)

        def hitung_kembalian(*_):
            try:
                diterima = int(uang_entry.get())
                total = self.selected["total"]
                if diterima >= total:
                    k = diterima - total
                    kembalian_lbl.config(
                        text=f"Kembalian: Rp{k:,}".replace(",", "."),
                        foreground="green"
                    )
                else:
                    kembalian_lbl.config(
                        text="Kembalian: Rp0",
                        foreground="red"
                    )
            except ValueError:
                kembalian_lbl.config(text="Kembalian: Rp0", foreground="black")

        uang_entry.bind("<KeyRelease>", hitung_kembalian)

        # ---- Action
        btn = tb.Frame(win)
        btn.pack(pady=15)

        tb.Button(
            btn, text="Bayar", bootstyle=SUCCESS,
            command=lambda: self.proses_bayar(win, uang_entry)
        ).pack(side=LEFT, padx=5)

        tb.Button(
            btn, text="Batal", bootstyle=SECONDARY,
            command=win.destroy
        ).pack(side=LEFT, padx=5)

    # ================= LOGIC =================
    def proses_bayar(self, win, uang_entry):
        try:
            diterima = int(uang_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Uang diterima harus angka")
            return

        total = self.selected["total"]
        if diterima < total:
            messagebox.showerror("Gagal", "Uang diterima kurang")
            return

        kembalian = diterima - total

        conn = get_connection()
        cur = conn.cursor()

        # Double check belum dibayar
        cur.execute("""
            SELECT 1 FROM pembayaran
            WHERE transaksi_id = ? AND jenis_transaksi = 'MEMBERSHIP'
        """, (self.selected["transaksi_id"],))
        if cur.fetchone():
            conn.close()
            messagebox.showinfo("Info", "Transaksi ini sudah lunas")
            win.destroy()
            return

        cur.execute("""
            INSERT INTO pembayaran
            (id, transaksi_id, jenis_transaksi, total, uang_diterima, kembalian, tanggal_bayar)
            VALUES (?, ?, 'MEMBERSHIP', ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            self.selected["transaksi_id"],
            total,
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
        self.load_transaksi()
