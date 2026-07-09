import json
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "dev-attendance-key"

DEFAULT_STUDENTS = [
    "Alice Johnson",
    "Bob Smith",
    "Charlie Brown",
    "Diana Prince",
    "Ethan Hunt",
    "Fiona Green",
    "George Miller",
]

DATA_DIR = Path(__file__).parent / "data"
ATTENDANCE_FILE = DATA_DIR / "attendance.json"
STUDENTS_FILE = DATA_DIR / "students.json"


def load_students():
    if not STUDENTS_FILE.exists():
        save_students(DEFAULT_STUDENTS)
        return list(DEFAULT_STUDENTS)
    with open(STUDENTS_FILE, encoding="utf-8") as f:
        return json.load(f)


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
    return render_template("index.html", students=students)


@app.route("/submit", methods=["POST"])
def submit():
    students = load_students()
    if not students:
        flash("Add at least one student before submitting attendance.", "error")
        return redirect(url_for("students"))

    records = {}
    for student in students:
        status = request.form.get(student, "absent")
        records[student] = status

    present_count = sum(1 for s in records.values() if s == "present")
    absent_count = len(records) - present_count

    record = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "records": records,
        "summary": {
            "present": present_count,
            "absent": absent_count,
            "total": len(records),
        },
    }
    save_record(record)

    return render_template("summary.html", record=record)


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
    if name in students:
        flash(f'"{name}" is already in the list.', "error")
        return redirect(url_for("students"))

    students.append(name)
    save_students(students)
    flash(f'Added "{name}".', "success")
    return redirect(url_for("students"))


@app.route("/students/delete", methods=["POST"])
def delete_student():
    name = request.form.get("name", "").strip()
    students = load_students()

    if name not in students:
        flash("Student not found.", "error")
        return redirect(url_for("students"))

    if len(students) <= 1:
        flash("Cannot delete the last student.", "error")
        return redirect(url_for("students"))

    students.remove(name)
    save_students(students)
    flash(f'Deleted "{name}".', "success")
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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
