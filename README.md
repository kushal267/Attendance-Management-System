# Face Identification and Attendance Management System

<p align="center">
  <img src="screenshots/main_gui.png" width="900">
</p>

## Overview

An AI-powered desktop application developed using Python for real-time face identification and automatic attendance management.

The system allows users to register faces, train deep learning embeddings, perform real-time recognition, and generate attendance reports in Excel format.

---

## Key Features

- Face Registration Module
- Automatic Dataset Generation
- DeepFace + FaceNet Embedding Training
- Real-Time Face Identification
- Automatic Attendance Marking
- Duplicate Attendance Prevention
- Eye Blink Detection Based Exit
- Attendance Database Management
- Excel Report Generation
- Windows Installer Support

---

## Technology Stack

| Technology | Purpose |
|------------|----------|
| Python | Core Development |
| OpenCV | Face Detection |
| DeepFace | Face Recognition |
| Mediapipe | Eye Blink Detection |
| SQLite | Database |
| Tkinter | GUI |
| Pandas | Excel Reports |
| PyInstaller | EXE Generation |
| Inno Setup | Installer Creation |

---

## System Workflow

```text
Student Registration
          ↓
Dataset Creation
          ↓
Model Training
          ↓
Real-Time Recognition
          ↓
Attendance Recording
          ↓
Excel Export
```

---
## Project structure



`registration.py` - captures face images from the webcam and stores them in `dataset/`

`training.py` - trains embeddings from images in `dataset/` and saves `face_model.pkl`

`recognition.py` - runs real-time face recognition and marks attendance in the SQLite database

`export_excel.py` - exports attendance data to `attendance/attendance.xlsx`

`database.py` - creates the `database/face_db.db` database and required tables

`attendance/` - output folder for exported Excel files

`database/` - SQLite database files

`dataset/` - student image folders, one folder per person

`haarcascade_frontalface_default.xml` - face detector model used by registration

# Application Screenshots
## Main Dashboard

![Main GUI](screenshots/main_gui.png)

## Student Registration

![Registration](screenshots/registration.png)

The administrator registers a new student and the system automatically captures facial images.

## Model Training

![Training](screenshots/training.png)

Facial embeddings are generated and stored inside the trained model.

## Real-Time Identification

![Recognition](screenshots/recognition.png)

The system performs real-time face recognition and automatically marks attendance.

## Attendance Database

![Attendance](screenshots/attendance.png)

Attendance records can be viewed directly from the application.

## Excel Export

![Export](screenshots/export_excel.png)

Attendance reports can be exported to Excel format.

# Automatic Data Storage

```text
Face_Attendance_Data/
│
├── attendance/
├── database/
├── dataset/
└── face_model.pkl
```

# Installation

## Clone Repository

```bash
git clone https://github.com/USERNAME/Face-Identification-Attendance-System.git
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Application

```bash
python src/gui.py
```

---

# Windows Installer

A professional Windows installer has been created using:

- PyInstaller
- Inno Setup

Installer can be downloaded from:

👉 Releases Section

---

# Future Enhancements

- Multi-user Authentication
- Web Dashboard
- Cloud Database
- Mobile Application
- Face Anti-Spoofing
- Attendance Analytics

---

# Project Information

**Implementation**

Implemented during industrial training at Supervisor Training Centre (STC), Northern Railway, Charbagh, Lucknow.

---

# Author

Kushal Patel

B.Tech Computer Science and Engineering

Feroze Gandhi Institute of Engineering and Technology

---

## License

This project is provided as-is for learning and personal use.
