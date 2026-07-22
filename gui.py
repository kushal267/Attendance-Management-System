import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['ABSL_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'



import warnings
import logging
warnings.filterwarnings('ignore', category=FutureWarning)
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('absl').setLevel(logging.ERROR)

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sqlite3
import datetime
import threading
import pickle
import cv2
import numpy as np
from PIL import Image, ImageTk
from tkinter import simpledialog
import glob
import time

try:
    import mediapipe as mp
    from mediapipe.python.solutions.face_mesh import FaceMesh
    MEDIAPIPE_IMPORT_ERROR = None
except Exception as exc:
    mp = None
    FaceMesh = None
    MEDIAPIPE_IMPORT_ERROR = str(exc)

try:
    from deepface import DeepFace
    DEEPFACE_ERROR = None
except Exception as e:
    DeepFace = None
    DEEPFACE_ERROR = str(e)
import sys
import os
from pathlib import Path
import ctypes

try:
    myappid = 'face.attendance.system.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

print("GUI Python =", sys.executable)
if getattr(sys, 'frozen', False):
    APP_DIR = sys._MEIPASS
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
USER_HOME = str(Path.home())
BASE_DIR = os.path.join(USER_HOME, "Documents", "Face_Attendance_Data")

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "dataset"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "attendance"), exist_ok=True)

DB_PATH = os.path.join(BASE_DIR, "database", "face_db.db")
# ---------------------------

# -----------------------------
# Window
# -----------------------------
root = tk.Tk()
root.title("Face Identification and Attendance Management System")
root.geometry("1200x760")
root.configure(bg="#EAF2F8")
root.resizable(False, False)
root.iconbitmap(os.path.join(APP_DIR, "icon.ico"))
# -----------------------------
# Colors
# -----------------------------
HEADER = "#F01616"
BTN = "#1ABC22"
BTN_HOVER = "#16A085"
BG = "#EAF2F8"


# -----------------------------
# Header
# -----------------------------
header = tk.Frame(root, bg=HEADER, height=80)
header.pack(fill="x")

title = tk.Label(
    header,
    text="FACE IDENTIFICATION AND ATTENDANCE MANAGEMENT SYSTEM",
    bg=HEADER,
    fg="white",
    font=("Arial", 22, "bold")
)
title.pack(pady=18)

# -----------------------------
# Clock
# -----------------------------
clock_label = tk.Label(
    root,
    font=("Arial", 14, "bold"),
    bg=BG,
    fg="black"
)
clock_label.place(x=920, y=90)


def update_clock():
    now = datetime.datetime.now()
    clock_label.config(
        text=now.strftime("%d-%m-%Y   %I:%M:%S %p")
    )
    root.after(1000, update_clock)


update_clock()

# -----------------------------
# Left Panel
# -----------------------------
left = tk.Frame(root, bg="#D6EAF8", width=300)
left.pack(side="left", fill="y")

# -----------------------------
# Status Label
# -----------------------------
status = tk.Label(
    left,
    text="STATUS : READY",
    bg="#D6EAF8",
    fg="green",
    font=("Arial", 12, "bold")
)

status.pack(pady=15)


def set_status(text):
    root.after(0, lambda: status.config(text=text))



def ensure_database():
    os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
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
    conn.commit()
    conn.close()

camera_photo = None
recognition_thread = None
recognition_stop_event = threading.Event()


# Functions
def register_face():

    reg = tk.Toplevel(root)
    reg.title("Register Student")
    reg.geometry("400x220")
    reg.resizable(False, False)
    reg.configure(bg="white")

    # Center window
    reg.update_idletasks()

    x = (reg.winfo_screenwidth() // 2) - (400 // 2)
    y = (reg.winfo_screenheight() // 2) - (220 // 2)

    reg.geometry(f"400x220+{x}+{y}")

    tk.Label(
        reg,
        text="Register New Student",
        font=("Arial",18,"bold"),
        bg="white"
    ).pack(pady=20)

    tk.Label(
        reg,
        text="Enter Student Name",
        font=("Arial",12),
        bg="white"
    ).pack()

    name_entry = tk.Entry(
        reg,
        font=("Arial",14),
        width=25
    )
    name_entry.pack(pady=15)

    name_entry.focus()

    def start_registration():

        name = name_entry.get().strip()

        if not name:
            messagebox.showwarning(
                "Warning",
                "Please enter name."
            )
            return

        reg.destroy()
        """ script_path = os.path.join(
        BASE_DIR,
        "registration.py"
        )

        subprocess.run(
        [
            sys.executable,
            script_path,
            name
        ]
      )"""
        def run_registration():

            import registration

            registration.register_faces(
            name,
            camera_callback=display_preview
            )
            def on_complete():
                camera_label.config(image="", text="Registration Completed")
                refresh_counts()
            root.after(0, on_complete)

        threading.Thread(target=run_registration, daemon=True).start()

        camera_label.config(
            image="",
            text="Registration Completed"
        )
        refresh_counts()

    tk.Button(
        reg,
        text="Start Registration",
        font=("Arial",12,"bold"),
        bg="#1ABC22",
        fg="white",
        width=18,
        command=start_registration
    ).pack(pady=10)
def train_model():
    def run_training():
        import training
        
 
        root.after(0, lambda: set_status("STATUS : Training Model... Please Wait"))
        
        try:

            training.train_model()
            
            root.after(0, lambda: messagebox.showinfo(
                "Training",
                "Model Training Completed"
            ))
        except Exception as exc:
    
            root.after(0, lambda: messagebox.showerror("Training Failed", str(exc)))
            
        finally:
         
            root.after(0, lambda: set_status("STATUS : READY"))

    threading.Thread(target=run_training, daemon=True).start()    
"""def train_model():
    import training

    training.train_model()
    set_status("STATUS : Training Model")
    
     script_path = os.path.join(BASE_DIR, "training.py")
    try:
        '''subprocess.run([sys.executable, script_path], check=True)'''
        messagebox.showinfo(
            "Training",
            "Model Training Completed"
        )
    except subprocess.CalledProcessError as exc:
        messagebox.showerror("Training Failed", f"Training script failed:\n{exc}")
    except Exception as exc:
        messagebox.showerror("Training Failed", str(exc))

    set_status("STATUS : READY")
    print("GUI Python :", sys.executable)
"""
def load_face_model():
    model_path = os.path.join(BASE_DIR, "face_model.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError("face_model.pkl not found. Train the model first.")
    with open(model_path, "rb") as f:
        data = pickle.load(f)
    if not isinstance(data, tuple):
        raise ValueError("face_model.pkl has unexpected data format")
    if len(data) == 3:
        return data
    if len(data) == 2:
        known_embeddings, known_names = data
        return known_embeddings, [-1] * len(known_names), known_names
    raise ValueError(f"face_model.pkl tuple length {len(data)} is not supported")


def cosine_distance(emb1, emb2):
    emb1 = np.array(emb1, dtype=np.float32)
    emb2 = np.array(emb2, dtype=np.float32)
    if np.linalg.norm(emb1) == 0 or np.linalg.norm(emb2) == 0:
        return 1.0
    return 1 - np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

def eye_ratio(points):

    vertical1 = np.linalg.norm(points[1]-points[5])

    vertical2 = np.linalg.norm(points[2]-points[4])

    horizontal = np.linalg.norm(points[0]-points[3])

    return (vertical1 + vertical2)/(2*horizontal)


def annotate_frame(img, results):
    for result in results:
        left, top, right, bottom = result["box"]
        name = result["name"]
        cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
        label_y = top - 10 if top - 10 > 10 else top + 25
        cv2.putText(img, name, (left, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    return img

def show_message(title, message, kind="info"):
    def _show():
        if kind == "error":
            messagebox.showerror(title, message)
        elif kind == "warning":
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)
    root.after(0, _show)


def display_preview(img):
    def _display():
        global camera_photo
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_img)
        image = image.resize((620, 460))
        camera_photo = ImageTk.PhotoImage(image)
        camera_label.config(image=camera_photo, text="")
    root.after(0, _display)

def recognition_worker():
    set_status("STATUS : Starting Recognition")

    try:
        known_embeddings, known_ids, known_names = load_face_model()
    except Exception as exc:
        show_message("Recognition Error", str(exc), "error")
        set_status("STATUS : READY")
        return

    if DeepFace is None:
        show_message("Recognition Error", "The DeepFace library is not installed. Install it with pip install deepface.", "error")
        set_status("STATUS : READY")
        return

    if not known_embeddings:
        show_message("Recognition Error", "No trained face embeddings found.", "error")
        set_status("STATUS : READY")
        return

    model_name = "Facenet"
    detector_backend = "opencv"
    threshold = 0.4
    frame_skip = 6
    resize_scale = 0.4
    shown_messages = set()
    results = []
    frame_count = 0

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

    eye_close_threshold = 0.23
    eye_close_timeout = 2.0
    eye_close_start_time = None

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        show_message("Recognition Error", "Cannot open webcam. Check your camera connection.", "error")
        set_status("STATUS : READY")
        return

    try:
        while not recognition_stop_event.is_set():
            ret, img = cam.read()
            if not ret or img is None:
                continue

            frame_count += 1
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            mesh_results = face_mesh.process(rgb)

            if frame_count % frame_skip == 0:
                small_img = cv2.resize(img, (0, 0), fx=resize_scale, fy=resize_scale)

                try:
                    representations = DeepFace.represent(
                        img_path=small_img,
                        model_name=model_name,
                        detector_backend=detector_backend,
                        enforce_detection=False,
                        align=False,
                    )
                except Exception:
                    representations = []

                results = []
                for rep in representations:
                    embedding = rep.get("embedding")
                    facial_area = rep.get("facial_area", {})
                    left = int(facial_area.get("x", 0) / resize_scale)
                    top = int(facial_area.get("y", 0) / resize_scale)
                    right = int((facial_area.get("x", 0) + facial_area.get("w", 0)) / resize_scale)
                    bottom = int((facial_area.get("y", 0) + facial_area.get("h", 0)) / resize_scale)

                    name = "Unknown"
                    user_id = None
                    if known_embeddings and embedding is not None:
                        distances = [cosine_distance(embedding, known_emb) for known_emb in known_embeddings]
                        best_index = int(np.argmin(distances))
                        best_distance = distances[best_index]
                        if best_distance <= threshold:
                            user_id = known_ids[best_index]
                            name = known_names[best_index]

                    display_name = name
                    if user_id is not None and user_id != -1:
                        display_name = f"{name} ({user_id})"

                    if name != "Unknown":
                        now = datetime.datetime.now()
                        date = now.strftime("%d-%m-%Y")
                        attendance_time = now.strftime("%H:%M:%S")

                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()

                        if user_id is not None and user_id != -1:
                            cursor.execute("SELECT * FROM attendance WHERE user_id=? AND date=?", (user_id, date))
                        else:
                            cursor.execute("SELECT * FROM attendance WHERE name=? AND date=?", (name, date))

                        record = cursor.fetchone()
                        if record is None:
                            cursor.execute(
                                "INSERT INTO attendance(user_id, name, date, time) VALUES(?,?,?,?)",
                                (user_id, name, date, attendance_time)
                            )
                            conn.commit()
                            if display_name not in shown_messages:
                                shown_messages.add(display_name)
                        else:
                            if display_name not in shown_messages:
                                shown_messages.add(display_name)

                        conn.close()

                    results.append({"box": (left, top, right, bottom), "name": display_name})

            if mesh_results.multi_face_landmarks:
                landmarks = mesh_results.multi_face_landmarks[0]
                h, w, _ = img.shape

                left_eye_idx = [33, 160, 158, 133, 153, 144]
                right_eye_idx = [362, 385, 387, 263, 373, 380]

                left_pts = []
                right_pts = []

                for idx in left_eye_idx:
                    x = int(landmarks.landmark[idx].x * w)
                    y = int(landmarks.landmark[idx].y * h)
                    left_pts.append([x, y])

                for idx in right_eye_idx:
                    x = int(landmarks.landmark[idx].x * w)
                    y = int(landmarks.landmark[idx].y * h)
                    right_pts.append([x, y])

                left_ear = eye_ratio(np.array(left_pts, dtype=np.float32))
                right_ear = eye_ratio(np.array(right_pts, dtype=np.float32))

                left_closed = left_ear < eye_close_threshold
                right_closed = right_ear < eye_close_threshold

                if left_closed and right_closed:
                    if eye_close_start_time is None:
                        eye_close_start_time = time.time()
                    elif time.time() - eye_close_start_time >= eye_close_timeout:
                        show_message("Recognition", "Attendance Marked", "info")
                        recognition_stop_event.set()
                        break
                else:
                    eye_close_start_time = None

                cv2.putText(
                    img,
                    f"L EAR: {left_ear:.2f}  R EAR: {right_ear:.2f}",
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                if eye_close_start_time is not None:
                    cv2.putText(
                        img,
                        f"Both eyes closed: {int(time.time() - eye_close_start_time)}s",
                        (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 0, 255),
                        2
                    )
                else:
                    cv2.putText(
                        img,
                        "Keep both eyes open",
                        (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )
            else:
                eye_close_start_time = None
                cv2.putText(
                    img,
                    "Face not detected",
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )

            annotated = annotate_frame(img.copy(), results)
            display_preview(annotated)

    finally:
        cam.release()
        if hasattr(face_mesh, "close"):
            face_mesh.close()
        root.after(0, lambda: camera_label.config(text="Camera will open during Recognition", image=""))
        set_status("STATUS : READY")


def start_attendance():
    global recognition_thread
    if recognition_thread is not None and recognition_thread.is_alive():
        messagebox.showwarning("Recognition", "Recognition is already running.")
        return
    recognition_stop_event.clear()
    recognition_thread = threading.Thread(target=recognition_worker, daemon=True)
    recognition_thread.start()


def stop_attendance():
    if recognition_thread is None or not recognition_thread.is_alive():
        return
    recognition_stop_event.set()
    set_status("STATUS : Stopping Recognition")


def export_excel():

    set_status("STATUS : Exporting Excel")

    script_path = os.path.join(
        BASE_DIR,
        "export_excel.py"
    )

    try:
        import export_excel

        export_excel.export_attendance()
        '''subprocess.run(
            [sys.executable, script_path],
            check=True
        )'''

        excel_path = os.path.join(
            BASE_DIR,
            "attendance",
            "attendance.xlsx"
        )

        if os.path.exists(excel_path):
            os.startfile(excel_path)

        messagebox.showinfo(
            "Excel",
            "Attendance Exported Successfully"
        )

    except Exception as e:
        messagebox.showerror(
            "Excel Export Failed",
            str(e)
        )

    set_status("STATUS : READY")

def refresh_counts():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.datetime.now().strftime("%d-%m-%Y")
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = ?", (today,))
    total = cursor.fetchone()[0] or 0

    attendance_lbl.config(
        text=f"Today's Attendance : {total}"
    )

    conn.close()

    students = 0
    dataset_dir = os.path.join(BASE_DIR, "dataset")
    if os.path.exists(dataset_dir):
        students = len([
            d for d in os.listdir(dataset_dir)
            if os.path.isdir(os.path.join(dataset_dir, d))
        ])

    students_lbl.config(
        text=f"Registered Students : {students}"
    )


def view_database():

    refresh_counts()

    win = tk.Toplevel(root)

    win.title("Attendance Database")

    win.geometry("700x400")

    tree = ttk.Treeview(
        win,
        columns=("ID", "Name", "Date", "Time"),
        show="headings"
    )

    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Date", text="Date")
    tree.heading("Time", text="Time")

    tree.pack(fill="both", expand=True)

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("SELECT id, name, date, time FROM attendance")

    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", tk.END, values=row)

    conn.close()


def reset_attendance():

    if messagebox.askyesno(
        "Confirm Reset",
        "Are you sure you want to clear all attendance records?"
    ):
        set_status("STATUS : Resetting Attendance")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM attendance")
        conn.commit()
        conn.close()

        refresh_counts()

        messagebox.showinfo(
            "Reset Attendance",
            "All attendance records have been cleared."
        )

        set_status("STATUS : READY")

        


# -----------------------------
# Button Style
# -----------------------------
def hover_in(e):
    e.widget["bg"] = BTN_HOVER


def hover_out(e):
    e.widget["bg"] = BTN


def create_button(text, command):

    btn = tk.Button(
        left,
        text=text,
        font=("Arial", 13, "bold"),
        bg=BTN,
        fg="white",
        width=22,
        height=2,
        command=command,
        relief="flat",
        cursor="hand2"
    )

    btn.pack(pady=10)

    btn.bind("<Enter>", hover_in)
    btn.bind("<Leave>", hover_out)

    return btn
 

create_button("Register Face", register_face)
create_button("Train Model", train_model)
create_button("Start Identification", start_attendance)
create_button("Stop Identification", stop_attendance)
create_button("View Attendance", view_database)
create_button("Export Excel", export_excel)
create_button("Reset Attendance", reset_attendance)
create_button("Exit", root.destroy)
# -----------------------------
# Right Panel
# -----------------------------
right = tk.Frame(root, bg=BG)
right.pack(fill="both", expand=True)

camera_box = tk.LabelFrame(
    right,
    text="Live Camera Preview",
    font=("Arial", 15, "bold"),
    width=660,
    height=520,
    bg="white"
)

camera_box.place(x=20, y=20)

camera_label = tk.Label(
    camera_box,
    text="Camera will open during Recognition",
    font=("Arial", 14),
    bg="white",
    bd=0
)

camera_label.place(x=20, y=20, width=620, height=460)

students_lbl = tk.Label(
    right,
    text="Registered Students : 0",
    font=("Arial", 15, "bold"),
    bg=BG
)

students_lbl.place(x=30, y=560)

attendance_lbl = tk.Label(
    right,
    text="Today's Attendance : 0",
    font=("Arial", 15, "bold"),
    bg=BG
)

attendance_lbl.place(x=30, y=600)

instruction_lbl = tk.Label(
    right,
    text="Close eyes for 2 seconds to stop identification",
    font=("Arial",12),
    bg=BG
)

instruction_lbl.place(
    x=30,
    y=640
)

ensure_database()
refresh_counts()

'''footer = tk.Label(
    root,
    text="Developed By : Kushal Patel",
    bg=HEADER,
    fg="white",
    font=("Arial", 11)
)

footer.pack(side="bottom", fill="x")'''

root.mainloop()