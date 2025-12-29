from datetime import datetime, date
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from database.db import get_connection

class DashboardMember(tb.Frame):
    def __init__(self, root, member_id):
        super().__init__(root)
        self.root = root
        self.member_id = member_id
        self.pack(fill=BOTH, expand=True)

        # Main Layout: Sidebar (Left) + Content (Right)
        self.sidebar = tb.Frame(self, bootstyle="secondary", width=250)
        self.sidebar.pack(side=LEFT, fill=Y)

        self.content = tb.Frame(self, bootstyle="light")
        self.content.pack(side=RIGHT, fill=BOTH, expand=True)

        self.create_sidebar()
        self.show_overview()

    # ================= SIDEBAR =================
    def create_sidebar(self):
        # Sidebar Container - Light/White background
        # Note: 'bg' argument works on standard Frames if bootstyle doesn't force it.
        # But 'light' bootstyle usually implies light gray/white.
        # We'll use a specific style or just default.
        
        # Profile / Avatar
        profile_frame = tb.Frame(self.sidebar) 
        profile_frame.pack(pady=40, padx=20, fill=X)
        
        # Icon / Initials
        tb.Label(
            profile_frame, 
            text="G", 
            bootstyle="primary", 
            font=("Helvetica", 40, "bold")
        ).pack(anchor=CENTER)

        tb.Label(
            profile_frame, 
            text="GYM MEMBER", 
            bootstyle="primary",
            font=("Helvetica", 12, "bold")
        ).pack(anchor=CENTER, pady=(5,0))
        
        # Navigation
        self.create_nav_btn("Dashboard", self.show_overview, "primary")
        self.create_nav_btn("My Classes", self.show_classes, "outline-primary")
        self.create_nav_btn("History", self.show_history, "outline-primary")
        
        # Divider
        ttk.Separator(self.sidebar, orient='horizontal').pack(fill=X, padx=20, pady=20)
        
        self.create_nav_btn("Logout", self.logout, "danger")

    def create_nav_btn(self, text, command, bootstyle):
        btn = tb.Button(
            self.sidebar,
            text=text,
            command=command,
            bootstyle=bootstyle,
            width=20
        )
        btn.pack(pady=5)

    def logout(self):
        self.destroy()
        from .login import Login
        Login(self.root)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # ================= PAGES =================
    def show_overview(self):
        self.clear_content()
        
        name, membership = self.get_member_info()
        
        # Header - White with Blue Text
        header = tb.Frame(self.content)
        header.pack(fill=X, padx=30, pady=30)
        
        tb.Label(
            header,
            text=f"Hello, {name}",
            font=("Helvetica", 28, "bold"),
            bootstyle="dark" # Black
        ).pack(anchor=W)
        
        tb.Label(
            header,
            text=f"{date.today().strftime('%A, %d %B %Y')}",
            font=("Helvetica", 14),
            bootstyle="secondary" # Gray
        ).pack(anchor=W)

        # Main Grid area
        grid_frame = tb.Frame(self.content)
        grid_frame.pack(fill=BOTH, expand=True, padx=30)
        
        # --- LEFT COL: Membership Card ---
        left_col = tb.Frame(grid_frame)
        left_col.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 15))
        
        self.create_membership_card(left_col, name, membership)
        
        # --- RIGHT COL: Actions ---
        right_col = tb.Frame(grid_frame)
        right_col.pack(side=LEFT, fill=BOTH, expand=True, padx=(15, 0))
        
        self.create_checkin_card(right_col)
        self.create_upcoming_class_card(right_col)

    def show_classes(self):
        self.clear_content()
        tb.Label(self.content, text="My Class Schedule", font=("Helvetica", 24, "bold"), bootstyle="primary").pack(padx=30, pady=30, anchor=W)
        
        scroll_container = tb.Frame(self.content)
        scroll_container.pack(fill=BOTH, expand=True, padx=30, pady=10)
        
        classes = self.get_my_classes()
        
        if not classes:
            tb.Label(scroll_container, text="No classes registered.", font=("Helvetica", 12)).pack(pady=20)
            return

        for c in classes:
            # Card with blue left border effect using Labelframe or Frame tricks
            card = tb.Frame(scroll_container, bootstyle="light", padding=15)
            card.pack(fill=X, pady=10)
            
            # Use a colored frame as a sidebar indicator
            indicator = tb.Frame(card, bootstyle="primary", width=5)
            indicator.pack(side=LEFT, fill=Y, padx=(0, 15))
            
            info_frame = tb.Frame(card)
            info_frame.pack(side=LEFT, fill=BOTH, expand=True)

            tb.Label(info_frame, text=c['nama_kelas'], font=("Helvetica", 14, "bold"), bootstyle="dark").pack(anchor=W)
            tb.Label(info_frame, text=f"{c['tanggal_kelas']} • {c['jam_kelas']}", font=("Helvetica", 11), bootstyle="primary").pack(anchor=W)
            tb.Label(info_frame, text=f"Trainer: {c['trainer']}", font=("Helvetica", 10), bootstyle="secondary").pack(anchor=W)

    def show_history(self):
        self.clear_content()
        tb.Label(self.content, text="Attendance History", font=("Helvetica", 24, "bold"), bootstyle="primary").pack(padx=30, pady=30, anchor=W)
        
        tree_frame = tb.Frame(self.content)
        tree_frame.pack(fill=BOTH, expand=True, padx=30, pady=10)
        
        y_scroll = tb.Scrollbar(tree_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)
        
        # Use 'primary' color for headings if possible via style, or just default
        tree = tb.Treeview(
            tree_frame, 
            columns=("tanggal", "in", "out"), 
            show="headings",
            yscrollcommand=y_scroll.set,
            style="primary.Treeview" # Blue headers
        )
        y_scroll.config(command=tree.yview)
        
        tree.heading("tanggal", text="Date")
        tree.heading("in", text="Clock In")
        tree.heading("out", text="Clock Out")
        
        tree.pack(fill=BOTH, expand=True)

        rows = self.get_absensi_data()
        for r in rows:
            tree.insert("", END, values=(r["tanggal"], r["jam_masuk"], r["jam_keluar"]))

    # ================= WIDGETS =================
    def create_membership_card(self, parent, name, membership):
        # Clean White Card with Blue Accents
        card = tb.Labelframe(parent, text="Membership Info", bootstyle="primary", padding=20)
        card.pack(fill=X, pady=10)
        
        # Member Name - Blue
        tb.Label(card, text=name.upper(), bootstyle="primary", font=("Helvetica", 16, "bold")).pack(anchor=W, pady=(10, 5))
        
        # ID - Black/Gray
        tb.Label(card, text=f"ID: {self.member_id}", bootstyle="secondary", font=("Courier New", 12)).pack(anchor=W)
        
        ttk.Separator(card, orient='horizontal').pack(fill=X, pady=15)
        
        # Status
        valid_until = membership['tanggal_berakhir'] if membership else "N/A"
        
        # Check active
        status_color = "success" if membership else "danger"
        status_text = "ACTIVE" if membership else "INACTIVE"
        
        row = tb.Frame(card)
        row.pack(fill=X)
        
        tb.Label(row, text="STATUS", bootstyle="secondary", font=("Helvetica", 8, "bold")).pack(side=LEFT)
        tb.Label(row, text=status_text, bootstyle=status_color, font=("Helvetica", 9, "bold")).pack(side=RIGHT)
        
        row2 = tb.Frame(card)
        row2.pack(fill=X, pady=(5,0))
        tb.Label(row2, text="VALID UNTIL", bootstyle="secondary", font=("Helvetica", 8, "bold")).pack(side=LEFT)
        tb.Label(row2, text=str(valid_until), bootstyle="dark", font=("Helvetica", 9, "bold")).pack(side=RIGHT)

    def create_checkin_card(self, parent):
        frame = tb.Labelframe(parent, text="Quick Entry", padding=15, bootstyle="success")
        frame.pack(fill=X, pady=10)
        
        tb.Label(frame, text="Record your daily activity.", font=("Helvetica", 9), bootstyle="secondary").pack(anchor=W, pady=5)
        
        btn_grp = tb.Frame(frame)
        btn_grp.pack(fill=X, pady=10)
        
        # Solid Blue for In, Outline for Out
        tb.Button(btn_grp, text="CLOCK IN", bootstyle="primary", width=15, command=self.clock_in).pack(side=LEFT, padx=5)
        tb.Button(btn_grp, text="CLOCK OUT", bootstyle="outline-primary", width=15, command=self.clock_out).pack(side=LEFT, padx=5)

    def create_upcoming_class_card(self, parent):
        frame = tb.Labelframe(parent, text="Next Class", padding=15, bootstyle="info")
        frame.pack(fill=X, pady=10)
        
        classes = self.get_my_classes()
        if classes:
             c = classes[0]
             # Blue Title
             tb.Label(frame, text=c['nama_kelas'], font=("Helvetica", 16, "bold"), bootstyle="primary").pack(anchor=W)
             tb.Label(frame, text=f"{c['tanggal_kelas']} @ {c['jam_kelas']}", font=("Helvetica", 11), bootstyle="dark").pack(anchor=W)
             tb.Label(frame, text=f"Trainer: {c['trainer']}", font=("Helvetica", 10), bootstyle="secondary").pack(anchor=W)
        else:
            tb.Label(frame, text="No upcoming classes.", font=("Helvetica", 10, "italic"), bootstyle="secondary").pack(anchor=W)

    # ================= LOGIC / DATA =================
    def get_member_info(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT nama FROM members WHERE id = ?", (self.member_id,))
        res = cur.fetchone()
        name = res["nama"] if res else "Unknown"
        
        cur.execute("""
            SELECT tanggal_mulai, tanggal_berakhir
            FROM transaksi_membership
            WHERE member_id = ?
            ORDER BY tanggal_mulai DESC
            LIMIT 1
        """, (self.member_id,))
        trx = cur.fetchone()
        conn.close()
        return name, trx

    def get_my_classes(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT k.nama_kelas, k.tanggal_kelas, k.jam_kelas, t.nama AS trainer
            FROM member_kelas mk
            JOIN kelas k ON mk.kelas_id = k.id
            JOIN trainers t ON k.trainer_id = t.id
            WHERE mk.member_id = ? AND k.tanggal_kelas >= ?
            ORDER BY k.tanggal_kelas ASC
        """, (self.member_id, date.today().isoformat()))
        rows = cur.fetchall()
        conn.close()
        return rows

    def get_absensi_data(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT tanggal, jam_masuk, jam_keluar
            FROM absensi
            WHERE member_id = ?
            ORDER BY tanggal DESC
        """, (self.member_id,))
        rows = cur.fetchall()
        conn.close()
        return rows

    def clock_in(self):
        today = date.today().isoformat()
        conn = get_connection()
        cur = conn.cursor()

        # CEK: apakah masih ada sesi yang BELUM clock out hari ini
        cur.execute("""
            SELECT 1
            FROM absensi
            WHERE member_id = ?
            AND tanggal = ?
            AND jam_keluar IS NULL
        """, (self.member_id, today))

        if cur.fetchone():
            messagebox.showinfo(
                "Info",
                "You must clock out before clocking in again."
            )
            conn.close()
            return

        now = datetime.now()
        cur.execute("""
            INSERT INTO absensi (id, member_id, tanggal, jam_masuk, jam_keluar)
            VALUES (?, ?, ?, ?, NULL)
        """, (
            f"ABS-{now.timestamp()}",
            self.member_id,
            today,
            now.strftime("%H:%M:%S")
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            f"Clock In Successful at {now.strftime('%H:%M:%S')}"
        )
        self.show_overview()

    def clock_out(self):
        today = date.today().isoformat()
        conn = get_connection()
        cur = conn.cursor()

        # Ambil sesi AKTIF terakhir hari ini
        cur.execute("""
            SELECT id
            FROM absensi
            WHERE member_id = ?
            AND tanggal = ?
            AND jam_keluar IS NULL
            ORDER BY jam_masuk DESC
            LIMIT 1
        """, (self.member_id, today))

        row = cur.fetchone()

        if not row:
            messagebox.showwarning(
                "Info",
                "No active session found. Please clock in first."
            )
            conn.close()
            return

        now_str = datetime.now().strftime("%H:%M:%S")
        cur.execute("""
            UPDATE absensi
            SET jam_keluar = ?
            WHERE id = ?
        """, (now_str, row["id"]))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            f"Clock Out Successful at {now_str}"
        )
        self.show_overview()

