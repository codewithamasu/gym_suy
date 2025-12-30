import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import Frame, Label
from database.db import get_connection
from .master_member import MasterMember
from .master_trainer import MasterTrainer
from .master_paket import MasterPaket
from .transaksi_membership import TransaksiMembership
from .pembayaran import PembayaranView
from .transaksi_harian import TransaksiHarianView
from .master_kelas import MasterKelas
from .member_kelas import MemberKelas
from .master_alat import MasterAlat
from datetime import date, datetime, timedelta
from utils.ui import set_app_icon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .transaksi_kelas import TransaksiKelas
import pandas as pd
from utils.session import SessionManager

class Dashboard:
    def __init__(self, root):
        self.root = root
        set_app_icon(self.root)
        # Main Layout container
        self.main_container = tb.Frame(root)
        self.main_container.pack(fill=BOTH, expand=True)

        # Sidebar (Light Gray/White)
        self.sidebar = tb.Frame(self.main_container, bootstyle="light", width=250)
        self.sidebar.pack(side=LEFT, fill=Y)

        # Content (White)
        self.content = tb.Frame(self.main_container, bootstyle="default")
        self.content.pack(side=RIGHT, fill=BOTH, expand=True)

        self.create_sidebar()
        self.show_dashboard()

    # ================= SIDEBAR =================
    def create_sidebar(self):
        # Sidebar Header
        header = tb.Frame(self.sidebar, bootstyle="light", padding=20)
        header.pack(fill=X)
        
        # Logo / Brand
        tb.Label(
            header,
            text="GYM ADMIN",
            font=("Helvetica", 20, "bold"),
            bootstyle="primary"
        ).pack(anchor=W)
        
        tb.Label(
            header,
            text="Management System",
            font=("Helvetica", 10),
            bootstyle="secondary"
        ).pack(anchor=W)

        # Show Current User (Encapsulation Getter)
        current_user = SessionManager.get_user()
        user_display = current_user.username if current_user else "Guest"
        
        tb.Label(
            header,
            text=f"Hi, {user_display}",
            font=("Helvetica", 10, "italic"),
            bootstyle="success"
        ).pack(anchor=W, pady=(5,0))

        # Navigation Menu
        # Group: Main
        self.create_menu_label("MAIN MENU")
        self.create_nav_button("Dashboard", "primary", self.show_dashboard)
        self.create_nav_button("Members", "outline-primary", self.show_member)
        self.create_nav_button("Classes", "outline-primary", self.show_kelas)
        self.create_nav_button("Trainers", "outline-primary", self.show_trainer)
        self.create_nav_button("Gym Tools", "outline-primary", self.show_alat)
        self.create_nav_button("Packages", "outline-primary", self.show_paket)

        # Group: Transaction
        self.create_menu_label("TRANSACTIONS")
        self.create_nav_button("Membership", "outline-primary", self.show_transaksi_membership)
        self.create_nav_button("Payment", "outline-primary", self.show_pembayaran)
        self.create_nav_button("Class Reg", "outline-primary", self.show_member_kelas)
        
        # Group: Report
        self.create_menu_label("REPORTS")
        self.create_nav_button("Daily Log", "outline-primary", self.show_transaksi_harian)
        self.create_nav_button("Attendance", "outline-primary", self.show_absensi)

        # Logout Button
        self.create_nav_button("Logout", "danger", self.logout)

    def create_menu_label(self, text):
        tb.Label(
            self.sidebar, 
            text=text, 
            bootstyle="secondary", 
            font=("Helvetica", 9, "bold")
        ).pack(anchor=W, padx=25, pady=(15, 5))

    def create_nav_button(self, text, style, command):
        btn = tb.Button(
            self.sidebar,
            text=text,
            bootstyle=style,
            width=25,
            command=command
        )
        btn.pack(pady=2, padx=10)

    def logout(self):
        SessionManager.clear_session()
        self.main_container.destroy()
        from .login import Login
        Login(self.root)

    # ================= CONTENT HANDLER =================
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_title(self, title):
        # Helper for other pages
        header = tb.Frame(self.content, padding=20)
        header.pack(fill=X)
        tb.Label(header, text=title, font=("Helvetica", 24, "bold"), bootstyle="primary").pack(anchor=W)

    # ================= PAGES =================
    def show_dashboard(self):
        self.clear_content()
        
        # Fetch Real Stats
        stats = self.get_dashboard_stats()
        
        # Header
        header = tb.Frame(self.content, padding=20)
        header.pack(fill=X)
        
        tb.Label(
            header, text="Dashboard Overview", 
            font=("Helvetica", 24, "bold"), bootstyle="primary"
        ).pack(anchor=W)
        
        tb.Label(
            header, text=f"Update: {date.today().strftime('%A, %d %B %Y')}", 
            font=("Helvetica", 11), bootstyle="secondary"
        ).pack(anchor=W)
        
        # Stats Grid
        stats_frame = tb.Frame(self.content, padding=20)
        stats_frame.pack(fill=X)
        
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        stats_frame.columnconfigure(3, weight=1)
        
        self.create_stat_card(stats_frame, "Total Members", stats['members'], "primary", 0)
        self.create_stat_card(stats_frame, "Trainers", stats['trainers'], "info", 1)
        self.create_stat_card(stats_frame, "Today's Income", f"Rp {stats['income']:,}", "success", 2)
        self.create_stat_card(stats_frame, "Visits Today", stats['visits'], "warning", 3)
        
        # Recent Activity / Quick Actions Section (Optional placeholder)
        self.create_charts(self.content)

    def create_stat_card(self, parent, title, value, color, col_index):
        # Card container
        card = tb.Frame(parent, bootstyle="light", padding=15)
        card.grid(row=0, column=col_index, sticky="ew", padx=10)
        
        # Title
        tb.Label(
            card, text=title.upper(), font=("Helvetica", 9, "bold"), 
            bootstyle="secondary"
        ).pack(anchor=W)
        
        # Value with dynamic color
        tb.Label(
            card, text=str(value), font=("Helvetica", 20, "bold"), 
            bootstyle=color
        ).pack(anchor=W, pady=(5,0))
        
        # Bottom bar decoration
        tb.Separator(card, bootstyle=color).pack(fill=X, pady=(10, 0))

    def get_dashboard_stats(self):
        conn = get_connection()
        cur = conn.cursor()
        
        # 1. Total Members
        cur.execute("SELECT COUNT(*) as count FROM members")
        members = cur.fetchone()['count']
        
        # 2. Total Trainers
        cur.execute("SELECT COUNT(*) as count FROM trainers")
        trainers = cur.fetchone()['count']
        
        # 3. Today's Revenue
        today = date.today().isoformat()
        cur.execute("""
            SELECT SUM(total) as total
            FROM pembayaran
            WHERE date(tanggal_bayar) = ?
        """, (today,))
        res_income = cur.fetchone()['total']
        income = res_income if res_income else 0
        
        # 4. Today's Visits
        cur.execute("""
            SELECT COUNT(*) as count
            FROM absensi
            WHERE tanggal = ?
        """, (today,))
        visits = cur.fetchone()['count']
        
        conn.close()
        
        return {
            "members": members,
            "trainers": trainers,
            "income": income,
            "visits": visits
        }


    # ================= CHARTS =================
    def get_chart_data(self):
        conn = get_connection()
        
        # Chart 1: Revenue Last 7 Days
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        df_rev = pd.read_sql_query(f"""
            SELECT tanggal_bayar, SUM(total) as revenue
            FROM pembayaran
            WHERE date(tanggal_bayar) BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY tanggal_bayar
            ORDER BY tanggal_bayar
        """, conn)
        
        # Chart 2: Peak Visit Hours (Absensi)
        df_visits = pd.read_sql_query("""
            SELECT strftime('%H', jam_masuk) as hour, COUNT(*) as count
            FROM absensi
            GROUP BY hour
            ORDER BY hour
        """, conn)

        # Chart 3: Membership Distribution (by Paket)
        df_dist = pd.read_sql_query("""
            SELECT p.durasi_bulan, COUNT(tm.id) as count
            FROM transaksi_membership tm
            JOIN paket_membership p ON tm.paket_id = p.id
            GROUP BY p.durasi_bulan
        """, conn)
        
        conn.close()
        return df_rev, df_visits, df_dist

    def create_charts(self, parent):
        chart_frame = tb.Frame(parent, padding=20)
        chart_frame.pack(fill=BOTH, expand=True)
        
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.columnconfigure(1, weight=1)
        
        df_rev, df_visits, df_dist = self.get_chart_data()

        # --- Chart 1: Revenue (Line) ---
        fig1, ax1 = plt.subplots(figsize=(5, 3), dpi=100)
        if not df_rev.empty:
            # ensure datetime dtype so we can format ticks compactly
            df_rev['tanggal_bayar'] = pd.to_datetime(df_rev['tanggal_bayar'])
            ax1.plot(df_rev['tanggal_bayar'], df_rev['revenue'], marker='o', color='#3498db', linewidth=2)
            ax1.fill_between(df_rev['tanggal_bayar'], df_rev['revenue'], color='#3498db', alpha=0.1)
            # format x-axis as DD-MM-YYYY to keep labels short
            import matplotlib.dates as mdates
            locator = mdates.AutoDateLocator()
            formatter = mdates.DateFormatter('%d-%m-%Y')
            ax1.xaxis.set_major_locator(locator)
            ax1.xaxis.set_major_formatter(formatter)
        ax1.set_title("Revenue Last 7 Days", fontsize=10, fontweight='bold', pad=10)
        ax1.tick_params(axis='x', rotation=45, labelsize=8)
        ax1.tick_params(axis='y', labelsize=8)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        plt.tight_layout()

        canvas1 = FigureCanvasTkAgg(fig1, master=chart_frame)
        canvas1.draw()
        canvas1.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        plt.close(fig1)

        # --- Chart 2: Peak Hours (Bar) ---
        fig2, ax2 = plt.subplots(figsize=(5, 3), dpi=100)
        if not df_visits.empty:
            ax2.bar(df_visits['hour'], df_visits['count'], color='#2ecc71', alpha=0.8)
        ax2.set_title("Peak Visit Hours", fontsize=10, fontweight='bold', pad=10)
        ax2.set_xlabel("Hour (24h)", fontsize=8)
        ax2.tick_params(axis='both', labelsize=8)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        plt.tight_layout()

        canvas2 = FigureCanvasTkAgg(fig2, master=chart_frame)
        canvas2.draw()
        canvas2.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        plt.close(fig2)
        
        # --- Chart 3: Distribution (Pie) --- (Optional)
        
        # Clean layouts logic
        chart_frame.rowconfigure(0, weight=1)

    def show_member(self):
        self.clear_content()
        MasterMember(self.content)

    def show_trainer(self):
        self.clear_content()
        MasterTrainer(self.content)

    def show_paket(self):
        self.clear_content()
        MasterPaket(self.content)

    def show_transaksi_harian(self):
        self.clear_content()
        TransaksiHarianView(self.content)

    def show_kelas(self):
        self.clear_content()
        MasterKelas(self.content)

    def show_alat(self):
        self.clear_content()
        MasterAlat(self.content)

    def show_transaksi_membership(self):
        self.clear_content()
        TransaksiMembership(self.content)

    def show_transaksi_kelas(self):
        self.clear_content()
        TransaksiKelas(self.content)


    def show_pembayaran(self):
        self.clear_content()
        PembayaranView(self.content)

    def show_absensi(self):
        self.clear_content()
        self.show_title("Absensi Member")

        tree = tb.Treeview(
            self.content,
            columns=("member", "tanggal", "masuk", "keluar"),
            show="headings"
        )

        tree.heading("member", text="Member")
        tree.heading("tanggal", text="Tanggal")
        tree.heading("masuk", text="Jam Masuk")
        tree.heading("keluar", text="Jam Keluar")

        tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT m.nama, a.tanggal, a.jam_masuk, a.jam_keluar
            FROM absensi a
            JOIN members m ON a.member_id = m.id
            ORDER BY a.tanggal DESC, a.jam_masuk DESC
        """)

        for r in cur.fetchall():
            tree.insert(
                "",
                END,
                values=(
                    r["nama"],
                    r["tanggal"],
                    r["jam_masuk"],
                    r["jam_keluar"]
                )
            )

        conn.close()

    def show_member_kelas(self):
        self.clear_content()
        MemberKelas(self.content)


