import sqlite3

conn = sqlite3.connect("database/face_db.db")
cur = conn.cursor()

cur.execute("DELETE FROM users")
cur.execute("DELETE FROM attendance")
cur.execute("DELETE FROM sqlite_sequence")

conn.commit()
conn.close()

print("Done")