import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import get_connection

conn = get_connection()
cur = conn.cursor()

# --- OPTION A: lihat user ke-15 (index mulai 0 -> OFFSET 14) ---
row = cur.execute("SELECT * FROM users ORDER BY ROWID LIMIT 1 OFFSET 14").fetchone()
print("Found (15th):", dict(row) if row else "No row at position 15")

# Jika ingin menghapus baris yang ditemukan:
if row:
    user_id = row["id"]
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    print("Deleted user id:", user_id)

# --- OPTION B: hapus langsung berdasarkan id literal (ganti '15' dengan id yang tepat) ---
# cur.execute("DELETE FROM users WHERE id = ?", ("15",))
# conn.commit()
# print("Deleted user id 15")

conn.close()