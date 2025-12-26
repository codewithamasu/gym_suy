import sqlite3
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "gym.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ================= USER =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # ================= MEMBER =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id TEXT PRIMARY KEY,
        nama TEXT NOT NULL,
        umur INTEGER,
        jenis_kelamin TEXT,
        status_aktif INTEGER DEFAULT 1
    )
    """)

    # ================= TRAINER =================
    cursor.execute("""
        CREATE TABLE IF NOT EXIST trainers (
        id TEXT PRIMARY KEY,
        nama TEXT NOT NULL,
        spesialisasi TEXT NOT NULL
            CHECK (spesialisasi IN (
                'Strength',
                'Cardio',
                'Yoga',
                'Rehabilitation'
            )),
        tarif_per_sesi INTEGER NOT NULL
    );
    """)

    # ================= PAKET MEMBERSHIP =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS paket_membership (
        id TEXT PRIMARY KEY,
        nama_paket TEXT NOT NULL,
        durasi_hari INTEGER NOT NULL,
        harga INTEGER NOT NULL
    )
    """)

    # ================= KELAS GYM =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kelas (
        id TEXT PRIMARY KEY,
        nama_kelas TEXT NOT NULL,
        kapasitas INTEGER NOT NULL,
        jadwal TEXT NOT NULL
    )
    """)

    # ================= ALAT GYM =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alat_gym (
        id TEXT PRIMARY KEY,
        nama_alat TEXT NOT NULL,
        kondisi TEXT NOT NULL
    )
    """)

    # ================= TRANSAKSI MEMBERSHIP =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transaksi_membership (
        id TEXT PRIMARY KEY,
        member_id TEXT NOT NULL,
        paket_id TEXT NOT NULL,
        tanggal_mulai TEXT NOT NULL,
        tanggal_berakhir TEXT NOT NULL,
        FOREIGN KEY (member_id) REFERENCES members(id),
        FOREIGN KEY (paket_id) REFERENCES paket_membership(id)
    )
    """)

    # ================= TRANSAKSI KELAS =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transaksi_kelas (
        id TEXT PRIMARY KEY,
        member_id TEXT NOT NULL,
        kelas_id TEXT NOT NULL,
        tanggal_daftar TEXT NOT NULL,
        FOREIGN KEY (member_id) REFERENCES members(id),
        FOREIGN KEY (kelas_id) REFERENCES kelas(id)
    )
    """)

    # ================= PEMBAYARAN =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pembayaran (
        id TEXT PRIMARY KEY,
        transaksi_id TEXT NOT NULL,
        jenis_transaksi TEXT NOT NULL,
        total INTEGER NOT NULL,
        tanggal_bayar TEXT NOT NULL
    )
    """)

    # ================= ABSENSI =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS absensi (
        id TEXT PRIMARY KEY,
        member_id TEXT NOT NULL,
        tanggal TEXT NOT NULL,
        jam_masuk TEXT NOT NULL,
        jam_keluar TEXT,
        FOREIGN KEY (member_id) REFERENCES members(id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database gym.db berhasil diinisialisasi.")


if __name__ == "__main__":
    init_db()
