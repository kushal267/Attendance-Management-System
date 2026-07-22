import sqlite3
import csv
import os
import datetime
from pathlib import Path

def export_attendance():
    USER_HOME = str(Path.home())
    BASE_DIR = os.path.join(USER_HOME, "Documents", "Face_Attendance_Data")
    db_path = os.path.join(BASE_DIR, "database", "face_db.db")
    attendance_folder = os.path.join(BASE_DIR, "attendance")
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    
 
    today_date = datetime.datetime.now().strftime("%d-%m-%Y")
    filename = f"Attendance_{today_date}.csv"
    export_path = os.path.join(attendance_folder, filename)
    
   
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance")
    rows = cursor.fetchall()
    
   
    cursor.execute("PRAGMA table_info(attendance)")
    columns = [col[1] for col in cursor.fetchall()]
    
   
    with open(export_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(columns) # Headers
        writer.writerows(rows)   # Data
        
    conn.close()
    
   
    os.startfile(export_path)

if __name__ == "__main__":
    export_attendance()