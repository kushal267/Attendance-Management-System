import sqlite3
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Delete dataset
dataset = BASE_DIR / "dataset"
if dataset.exists():
    shutil.rmtree(dataset)
dataset.mkdir(exist_ok=True)

# Delete model
model = BASE_DIR / "face_model.pkl"
if model.exists():
    model.unlink()

# Delete attendance excel
excel = BASE_DIR / "attendance" / "attendance.xlsx"
if excel.exists():
    excel.unlink()

# Reset DB
db = BASE_DIR / "database" / "face_db.db"

conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("DELETE FROM users")
cur.execute("DELETE FROM attendance")

cur.execute("DELETE FROM sqlite_sequence WHERE name='users'")
cur.execute("DELETE FROM sqlite_sequence WHERE name='attendance'")

conn.commit()
conn.close()

print("Project completely reset.")