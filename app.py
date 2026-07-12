import json
from datetime import datetime
import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "dev-attendance-key"

DEFAULT_STUDENTS = [
    {"name": "Alice Johnson", "roll_no": 1},
    {"name": "Bob Smith", "roll_no": 2},
    {"name": "Charlie Brown", "roll_no": 3},
    {"name": "Diana Prince", "roll_no": 4},
    {"name": "Ethan Hunt", "roll_no": 5},
    {"name": "Fiona Green", "roll_no": 6},
    {"name": "George Miller", "roll_no": 7},
]

DATA_DIR = Path(__file__).parent / "data"
ATTENDANCE_FILE = DATA_DIR / "attendance.json"
STUDENTS_FILE = DATA_DIR / "students.json"


def get_next_roll_no(students):
    """Get the next available roll number"""
    if not students:
        return 1
    return max(student["roll_no"] for student in students) + 1


def load_students():
    if not STUDENTS_FILE.exists():
        save_students(DEFAULT_STUDENTS)
        return list(DEFAULT_STUDENTS)
    with open(STUDENTS_FILE, encoding="utf-8") as f:
        students = json.load(f)
        # Handle old format (list of strings) by converting to new format
        if students and isinstance(students[0], str):
            students = [{"name": name, "roll_no": i+1} for i, name in enumerate(students)]
            save_students(students)
        return students


def save_students(students):
    DATA_DIR.mkdir(exist_ok=True)
    with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=2)


def load_records():
    if not ATTENDANCE_FILE.exists():
        return []
    with open(ATTENDANCE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_record(record):
    DATA_DIR.mkdir(exist_ok=True)
    records = load_records()
    records.append(record)
    save_records(records)


def save_records(records):
    DATA_DIR.mkdir(exist_ok=True)
    with open(ATTENDANCE_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def delete_record(date, time):
    records = load_records()
    updated = [r for r in records if not (r["date"] == date and r["time"] == time)]
    if len(updated) == len(records):
        return False
    save_records(updated)
    return True


@app.route("/")
def index():
    students = load_students()
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    current_time = datetime.now().strftime("%I:%M %p")
    # Create a mapping of student names to their info for easy access
    student_map = {s["name"]: s for s in students}
    return render_template("index.html", students=students, student_map=student_map, current_date=current_date, current_time=current_time)


@app.route("/submit", methods=["POST"])
def submit():
    students = load_students()
    if not students:
        flash("Add at least one student before submitting attendance.", "error")
        return redirect(url_for("students"))

    records = {}
    for student in students:
        student_name = student["name"]
        status = request.form.get(student_name, "absent")
        records[student_name] = status

    present_count = sum(1 for s in records.values() if s == "present")
    absent_count = len(records) - present_count

    # Create student map for display
    student_map = {s["name"]: s for s in students}

    record = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "records": records,
        "student_map": student_map,
        "summary": {
            "present": present_count,
            "absent": absent_count,
            "total": len(records),
        },
    }
    save_record(record)

    return render_template("summary.html", record=record, student_map=student_map)


@app.route("/students")
def students():
    return render_template("students.html", students=load_students())


@app.route("/students/add", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Please enter a student name.", "error")
        return redirect(url_for("students"))

    students = load_students()
    # Check if student name already exists
    if any(s["name"] == name for s in students):
        flash(f'"{name}" is already in the list.', "error")
        return redirect(url_for("students"))

    # Generate next roll number
    next_roll_no = get_next_roll_no(students)
    students.append({"name": name, "roll_no": next_roll_no})
    save_students(students)
    flash(f'Added "{name}" with Roll No. {next_roll_no}.', "success")
    return redirect(url_for("students"))


@app.route("/students/delete", methods=["POST"])
def delete_student():
    name = request.form.get("name", "").strip()
    students = load_students()

    student_to_delete = None
    for s in students:
        if s["name"] == name:
            student_to_delete = s
            break

    if student_to_delete is None:
        flash("Student not found.", "error")
        return redirect(url_for("students"))

    if len(students) <= 1:
        flash("Cannot delete the last student.", "error")
        return redirect(url_for("students"))

    students = [s for s in students if s["name"] != name]
    save_students(students)
    flash(f'Deleted "{name}" (Roll No. {student_to_delete["roll_no"]}).', "success")
    return redirect(url_for("students"))


@app.route("/history")
def history():
    records = load_records()
    records = list(reversed(records))
    return render_template("history.html", records=records)


@app.route("/history/delete", methods=["POST"])
def delete_history():
    date = request.form.get("date", "").strip()
    time = request.form.get("time", "").strip()

    if not date or not time:
        flash("Invalid attendance record.", "error")
        return redirect(url_for("history"))

    if delete_record(date, time):
        flash(f"Deleted attendance for {date} at {time}.", "success")
    else:
        flash("Attendance record not found.", "error")

    return redirect(url_for("history"))

port = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=False)
