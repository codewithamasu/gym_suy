import sqlite3
import uuid
from datetime import datetime, timedelta

DB_NAME = "gym.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def seed_users(cursor):
    users = [
        ("admin", "admin123", "ADMIN"),
        ("kasir", "kasir123", "KASIR"),
        ("staff", "staff123", "STAFF"),
    ]

    for username, password, role in users:
        cursor.execute("""
        INSERT OR IGNORE INTO users (id, username, password, role)
        VALUES (?, ?, ?, ?)
        """, (str(uuid.uuid4()), username, password, role))


def seed_members(cursor):
    members = [
        ("Andi", 22, "L"),
        ("Budi", 25, "L"),
        ("Citra", 23, "P"),
        ("Dewi", 27, "P"),
        ("Eko", 30, "L"),
    ]

    for nama, umur, jk in members:
        cursor.execute("""
        INSERT OR IGNORE INTO members (id, nama, umur, jenis_kelamin)
        VALUES (?, ?, ?, ?)
        """, (str(uuid.uuid4()), nama, umur, jk))


def seed_trainers(cursor):
    trainers = [
        ("Rizal", "Strength", 150000),
        ("Sinta", "Yoga", 120000),
        ("Fajar", "Cardio", 130000),
    ]

    for nama, spesialisasi, tarif in trainers:
        cursor.execute("""
        INSERT OR IGNORE INTO trainers (id, nama, spesialisasi, tarif_per_sesi)
        VALUES (?, ?, ?, ?)
        """, (str(uuid.uuid4()), nama, spesialisasi, tarif))


def seed_paket(cursor):
    paket = [
        ("Bulanan", 30, 300000),
        ("3 Bulan", 90, 800000),
        ("Tahunan", 365, 2800000),
    ]

    for nama, durasi, harga in paket:
        cursor.execute("""
        INSERT OR IGNORE INTO paket_membership (id, jenis_paket, durasi, harga)
        VALUES (?, ?, ?, ?)
        """, (str(uuid.uuid4()), nama, durasi, harga))


def seed_kelas(cursor):
    kelas = [
        ("Yoga", 10, "Senin 07:00"),
        ("Zumba", 15, "Rabu 18:00"),
        ("CrossFit", 8, "Jumat 17:00"),
    ]

    for nama, kapasitas, jadwal in kelas:
        cursor.execute("""
        INSERT OR IGNORE INTO kelas (id, nama_kelas, kapasitas, jadwal)
        VALUES (?, ?, ?, ?)
        """, (str(uuid.uuid4()), nama, kapasitas, jadwal))


def seed_alat(cursor):
    alat = [
        ("Treadmill", "Baik"),
        ("Bench Press", "Baik"),
        ("Dumbbell", "Baik"),
        ("Sepeda Statis", "Maintenance"),
    ]

    for nama, kondisi in alat:
        cursor.execute("""
        INSERT OR IGNORE INTO alat_gym (id, nama_alat, kondisi)
        VALUES (?, ?, ?)
        """, (str(uuid.uuid4()), nama, kondisi))


def seed_transaksi(cursor):
    member = cursor.execute("SELECT id FROM members LIMIT 1").fetchone()
    paket = cursor.execute("SELECT id FROM paket_membership LIMIT 1").fetchone()
    kelas = cursor.execute("SELECT id FROM kelas LIMIT 1").fetchone()

    if not member or not paket or not kelas:
        return

    today = datetime.now().date()
    end_date = today + timedelta(days=30)

    # Transaksi membership
    cursor.execute("""
    INSERT OR IGNORE INTO transaksi_membership
    (id, member_id, paket_id, tanggal_mulai, tanggal_berakhir)
    VALUES (?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        member["id"],
        paket["id"],
        today.isoformat(),
        end_date.isoformat()
    ))

    # Transaksi kelas
    cursor.execute("""
    INSERT OR IGNORE INTO transaksi_kelas
    (id, member_id, kelas_id, tanggal_daftar)
    VALUES (?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        member["id"],
        kelas["id"],
        today.isoformat()
    ))


def seed_pembayaran(cursor):
    transaksi = cursor.execute("""
    SELECT id FROM transaksi_membership LIMIT 1
    """).fetchone()

    if not transaksi:
        return

    cursor.execute("""
    INSERT OR IGNORE INTO pembayaran
    (id, transaksi_id, jenis_transaksi, total, tanggal_bayar)
    VALUES (?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        transaksi["id"],
        "MEMBERSHIP",
        300000,
        datetime.now().isoformat()
    ))


def seed_absensi(cursor):
    member = cursor.execute("SELECT id FROM members LIMIT 1").fetchone()
    if not member:
        return

    cursor.execute("""
    INSERT OR IGNORE INTO absensi
    (id, member_id, tanggal, jam_masuk)
    VALUES (?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        member["id"],
        datetime.now().date().isoformat(),
        datetime.now().time().strftime("%H:%M")
    ))


def main():
    conn = get_connection()
    cursor = conn.cursor()

    seed_users(cursor)
    seed_members(cursor)
    seed_trainers(cursor)
    seed_paket(cursor)
    seed_kelas(cursor)
    seed_alat(cursor)
    seed_transaksi(cursor)
    seed_pembayaran(cursor)
    seed_absensi(cursor)

    conn.commit()
    conn.close()
    print("Dummy data berhasil di-seed.")


if __name__ == "__main__":
    main()
