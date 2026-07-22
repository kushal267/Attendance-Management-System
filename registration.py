import os
import sqlite3
import sys
from pathlib import Path
import cv2
import time
def get_base_dir():
    from pathlib import Path
    
    data_dir = Path.home() / "Documents" / "Face_Attendance_Data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir
"""
def get_base_dir():
    if getattr(sys, "frozen", False) and getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS)
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

"""
def register_faces(
        name,
        camera_callback=None,
        base_dir=None,
        max_images=50):
    if not name or not name.strip():
        raise ValueError("Name cannot be empty.")

    clean_name = name.strip()
    safe_name = clean_name.replace(" ", "_")
    base_dir = Path(base_dir) if base_dir is not None else get_base_dir()

    dataset_dir = base_dir / "dataset"
    database_dir = base_dir / "database"
    dataset_dir.mkdir(exist_ok=True)
    database_dir.mkdir(exist_ok=True)

    db_path = database_dir / "face_db.db"
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dataset_path TEXT
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            date TEXT,
            time TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)
        cursor.execute("PRAGMA table_info(attendance)")
        attendance_columns = [row[1] for row in cursor.fetchall()]
        if "user_id" not in attendance_columns:
            cursor.execute("ALTER TABLE attendance ADD COLUMN user_id INTEGER")

        cursor.execute("INSERT INTO users (name) VALUES (?)", (clean_name,))
        user_id = cursor.lastrowid
        folder_name = f"{user_id}_{safe_name}"
        path = dataset_dir / folder_name
        cursor.execute(
            "UPDATE users SET dataset_path = ? WHERE user_id = ?",
            (str(path), user_id)
        )
        conn.commit()
    finally:
        conn.close()

    path.mkdir(exist_ok=True)

    if getattr(sys, 'frozen', False):
        cascade_dir = sys._MEIPASS
    else:
        cascade_dir = os.path.dirname(os.path.abspath(__file__))
    
    cascade_path = os.path.join(cascade_dir, "haarcascade_frontalface_default.xml")
    
    if not os.path.exists(cascade_path):
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        
    face_detector = cv2.CascadeClassifier(cascade_path)

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        raise RuntimeError("Cannot open webcam. Check camera connection.")

    count = 0
    try:
        while True:
            ret, img = cam.read()
            if not ret or img is None:
                raise RuntimeError("Failed to read a frame from webcam")

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                count += 1

                cv2.imwrite(str(path / f"{count}.jpg"), gray[y:y + h, x:x + w])
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

            if camera_callback is not None:
                camera_callback(img)
                time.sleep(0.1)  
            else:
                cv2.imshow("Register Face", img)

            if cv2.waitKey(10) & 0xFF == 27:  
                break
            if count >= max_images:
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()

    return path


def main():
    if len(sys.argv) > 1:
        name = sys.argv[1].strip()
    else:
        print("Name not provided.")
        return 1

    try:
        register_faces(name)
        print("Face Registered")
        return 0
    except Exception as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
if __name__ == "__main__":
    if len(sys.argv) > 1:
        register_faces(sys.argv[1])
    else:
        print("Name not provided")