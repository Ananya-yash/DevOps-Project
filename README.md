# Student Attendance System

A Flask web app to mark daily student attendance, view summaries, and manage records.

## Project Structure

```
DevOps_Project/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── static/
│   └── style.css           # Stylesheets
├── templates/
│   ├── base.html           # Shared layout
│   ├── index.html          # Take attendance page
│   ├── summary.html        # Attendance summary after submit
│   ├── history.html        # Past attendance records
│   └── students.html       # Add/delete students
└── data/
    ├── students.json       # Student list (auto-created)
    └── attendance.json     # Attendance records (auto-created)
```

## Setup & Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## Features

- Mark students as Present or Absent
- Submit and view attendance summary
- Add and delete students
- View and delete past attendance records
