from database.db import get_connection
from utils.auth import hash_password
import uuid

conn = get_connection()
cur = conn.cursor()

cur.execute("""
    INSERT INTO users (id, username, password, role)
    VALUES (?, ?, ?, 'ADMIN')
""", (str(uuid.uuid4()), 'admin', hash_password('admin123')))

conn.commit()
conn.close()
