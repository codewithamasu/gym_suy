from datetime import datetime, date
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection


class Absensi(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)

        self.create_widgets()
        self.load_members()
        self.load_absensi()

    # ================= UI =================
    def create_widgets(self):
        # HEADER
        header_frame = tb.Frame(self)
        header_frame.pack(fill=X, padx=20, pady=20)
        tb.Label(
            header_frame,
            text="Menu Absensi Member",
            font=("Helvetica", 18, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)

        # FORM CONTAINER
        form_frame = tb.Labelframe(self, text="Catat Kehadiran", padding=20, bootstyle="primary")
        form_frame.pack(fill=X, padx=20, pady=5)
        
        form_frame.columnconfigure(1, weight=1)

        # Row 0
        tb.Label(form_frame, text="Pilih Member:").grid(row=0, column=0, sticky=W, padx=10, pady=10)
        self.member_combo = tb.Combobox(form_frame, state="readonly")
        self.member_combo.grid(row=0, column=1, sticky=EW, padx=10)

        # BUTTONS
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill=X, padx=20, pady=20)
        
        tb.Button(
            btn_frame, text="Clock In (Masuk)", bootstyle="success", command=self.clock_in
        ).pack(side=LEFT, padx=5)

        tb.Button(
            btn_frame, text="Clock Out (Keluar)", bootstyle="warning", command=self.clock_out
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
            columns=("member", "tanggal", "masuk", "keluar"),
            show="headings",
            yscrollcommand=y_scroll.set,
            style="primary.Treeview"
        )
        y_scroll.config(command=self.tree.yview)

        self.tree.heading("member", text="Member")
        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("masuk", text="Jam Masuk")
        self.tree.heading("keluar", text="Jam Keluar")
        
        self.tree.column("member", width=200)

        self.tree.pack(fill=BOTH, expand=True)

    # ================= LOAD =================
    def load_members(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nama FROM members")

        self.member_map = {}
        values = []

        for m in cur.fetchall():
            self.member_map[m["nama"]] = m["id"]
            values.append(m["nama"])

        self.member_combo["values"] = values
        conn.close()

    def load_absensi(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT a.id, m.nama, a.tanggal, a.jam_masuk, a.jam_keluar
            FROM absensi a
            JOIN members m ON a.member_id = m.id
            ORDER BY a.tanggal DESC
        """)

        for r in cur.fetchall():
            self.tree.insert(
                "",
                END,
                iid=r["id"],
                values=(r["nama"], r["tanggal"], r["jam_masuk"], r["jam_keluar"])
            )
        conn.close()

    # ================= VALIDASI =================
    def has_active_membership(self, member_id):
        today = date.today().isoformat()
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 1 FROM transaksi_membership
            WHERE member_id = ?
            AND ? BETWEEN tanggal_mulai AND tanggal_berakhir
        """, (member_id, today))

        active = cur.fetchone() is not None
        conn.close()
        return active

    def has_clocked_in_today(self, member_id):
        today = date.today().isoformat()
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id FROM absensi
            WHERE member_id = ? AND tanggal = ?
        """, (member_id, today))

        row = cur.fetchone()
        conn.close()
        return row

    # ================= ACTION =================
    def clock_in(self):
        member_name = self.member_combo.get()
        if not member_name:
            messagebox.showwarning("Validasi", "Pilih member")
            return

        member_id = self.member_map.get(member_name)

        if not self.has_active_membership(member_id):
            messagebox.showerror("Ditolak", "Membership tidak aktif")
            return

        if self.has_clocked_in_today(member_id):
            messagebox.showwarning("Info", "Member sudah clock in hari ini")
            return

        now = datetime.now()
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO absensi (id, member_id, tanggal, jam_masuk)
            VALUES (?, ?, ?, ?)
        """, (
            f"ABS-{now.timestamp()}",
            member_id,
            now.date().isoformat(),
            now.strftime("%H:%M:%S")
        ))

        conn.commit()
        conn.close()
        self.load_absensi()

    def clock_out(self):
        member_name = self.member_combo.get()
        if not member_name:
            messagebox.showwarning("Validasi", "Pilih member")
            return

        member_id = self.member_map.get(member_name)
        today = date.today().isoformat()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, jam_keluar FROM absensi
            WHERE member_id = ? AND tanggal = ?
        """, (member_id, today))

        row = cur.fetchone()
        if not row:
            messagebox.showwarning("Info", "Belum clock in hari ini")
            conn.close()
            return

        if row["jam_keluar"]:
            messagebox.showwarning("Info", "Sudah clock out")
            conn.close()
            return

        cur.execute("""
            UPDATE absensi
            SET jam_keluar = ?
            WHERE id = ?
        """, (
            datetime.now().strftime("%H:%M:%S"),
            row["id"]
        ))

        conn.commit()
        conn.close()
        self.load_absensi()

    # ================= EXPORT =================
    def export_csv(self):
        try:
            import pandas as pd
            from tkinter import filedialog
            
            conn = get_connection()
            query = """
                SELECT a.id, m.nama AS Member, a.tanggal, a.jam_masuk, a.jam_keluar
                FROM absensi a
                JOIN members m ON a.member_id = m.id
                ORDER BY a.tanggal DESC
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                messagebox.showinfo("Info", "Tidak ada data untuk diexport.")
                return

            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="Simpan Laporan Absensi"
            )
            
            if filename:
                df.to_csv(filename, index=False)
                messagebox.showinfo("Sukses", f"Data berhasil diexport ke:\n{filename}")
                
        except ImportError:
            messagebox.showerror("Error", "Modul 'pandas' belum terinstall.")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export data: {str(e)}")
