from flask import Flask, request, jsonify, render_template, redirect, url_for
import pyodbc
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

# -----------------------------------------
# DATABASE CONNECTION
# -----------------------------------------
def get_connection():
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={os.getenv('SQL_DATABASE')};"
        f"UID={os.getenv('SQL_USERNAME')};"
        f"PWD={os.getenv('SQL_PASSWORD')};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return pyodbc.connect(connection_string)

# -----------------------------------------
# ROUTES FOR PAGES
# -----------------------------------------

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/students-page")
def students_page():
    return render_template("students.html")

# -----------------------------------------
# LOGIN CHECK (STATIC)
# -----------------------------------------

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    if data["username"] == "admin" and data["password"] == "admin123":
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid credentials"})

# -----------------------------------------
# CRUD API FOR StudentMarks
# -----------------------------------------

# GET all students
@app.route("/api/students", methods=["GET"])
def get_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM StudentMarks")
    rows = cursor.fetchall()

    students = []
    for r in rows:
        students.append({
            "StudentID": r.StudentID,
            "Name": r.Name,
            "Semester": r.Semester,
            "Subject": r.Subject,
            "Marks": r.Marks,
            "TotalMarks": r.TotalMarks
        })

    conn.close()
    return jsonify(students)

# ADD student
@app.route("/api/students", methods=["POST"])
def add_student():
    try:
        data = request.get_json()  # <-- IMPORTANT
    except:
        return jsonify({"error":"Invalid JSON"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO StudentMarks (Name, Semester, Subject, Marks, TotalMarks)
        VALUES (?, ?, ?, ?, ?)
    """, (data["Name"], data["Semester"], data["Subject"], data["Marks"], data["TotalMarks"]))

    conn.commit()
    conn.close()

    return jsonify({"message": "Student added successfully!"})


@app.route("/logout")
def logout():
    return redirect("/login")


# UPDATE student
@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE StudentMarks
        SET Name=?, Semester=?, Subject=?, Marks=?, TotalMarks=?
        WHERE StudentID=?
    """, (data["Name"], data["Semester"], data["Subject"],
          data["Marks"], data["TotalMarks"], student_id))

    conn.commit()
    conn.close()
    return jsonify({"message": "Student updated successfully!"})

# DELETE student
@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM StudentMarks WHERE StudentID=?", (student_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Student deleted successfully!"})

# -----------------------------------------
# FILTER ROUTE
# -----------------------------------------

@app.route("/api/filter", methods=["GET"])
def filter_students():
    subject = request.args.get("subject")
    semester = request.args.get("semester")

    query = "SELECT * FROM StudentMarks WHERE 1=1"
    params = []

    if subject:
        query += " AND Subject=?"
        params.append(subject)

    if semester:
        query += " AND Semester=?"
        params.append(semester)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)

    rows = cursor.fetchall()

    results = [{
        "StudentID": r.StudentID,
        "Name": r.Name,
        "Semester": r.Semester,
        "Subject": r.Subject,
        "Marks": r.Marks,
        "TotalMarks": r.TotalMarks
    } for r in rows]

    conn.close()
    return jsonify(results)

# -----------------------------------------
# RUN APP
# -----------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
