"""
CEFR Placement Test - Knowledge Grid Academy
Full version with: timer, admin auth, centers, enrollment, Excel export
"""
import json
import sqlite3
import hashlib
import random
import string
import csv
import io
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, make_response, send_file
)
from openpyxl import Workbook

# ---------------------------------------------------------
# 1. CREATE THE APP OBJECT FIRST
# ---------------------------------------------------------
app = Flask(__name__)
app.secret_key = "kg-academy-cefr-2026-change-in-production"

# ---------------------------------------------------------
# 2. THEN ADD THE TEMPLATE FILTER
# ---------------------------------------------------------
@app.template_filter('format_time')
def format_time_filter(seconds):
    """Formats seconds into 'Xm Ys' or 'Xh Ym'."""
    if not seconds:
        return "-"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m {s}s"

# ---------------------------------------------------------
# 3. REST OF YOUR CONFIG
# ---------------------------------------------------------
DB_PATH = "cefr_test.db"

# 10 KG Academy branches
CENTERS = [
    "KG Academy - Al-Khuwair",
    "KG Academy - Galah",
    "KG Academy - Salalah",
    "KG Academy - Nimr",
    "KG Academy - Sohar",
    "KG Academy - Sur",
    "KG Academy - Suwaiq",
    "KG Academy - Rima",
    "KG Academy - Marmul",
    "KG Academy - Fahud",
]

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def generate_user_id() -> str:
    """Auto-generate unique user ID like KG-2026-XXXX."""
    year = datetime.now().year
    while True:
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        uid = f"KG-{year}-{suffix}"
        conn = get_db()
        exists = conn.execute("SELECT id FROM users WHERE user_id=?", (uid,)).fetchone()
        conn.close()
        if not exists:
            return uid


def get_cefr_mapping(score):
    mapping = [
        (0,  5,  "A0",  "Module 1: Beginners - 1"),
        (6,  10, "A0",  "Module 2: Beginners - 2"),
        (11, 15, "A1",  "Module 3: Elementary - 1"),
        (16, 20, "A2",  "Module 4: Elementary - 2"),
        (21, 25, "B1",  "Module 5: Pre-Intermediate - 1"),
        (26, 30, "B1",  "Module 6: Pre-Intermediate - 2"),
        (31, 35, "B1+", "Module 7: Intermediate - 1"),
        (36, 40, "B2",  "Module 8: Intermediate - 2"),
        (41, 45, "B2+", "Module 9: Upper-Intermediate - 1"),
        (46, 50, "B2+", "Module 10: Upper-Intermediate - 2"),
    ]
    for low, high, level, module in mapping:
        if low <= score <= high:
            return level, module
    return "N/A", "N/A"


def get_questions():
    conn = get_db()
    rows = conn.execute("SELECT * FROM questions ORDER BY question_number").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ------------------------------------------------------------------
# Routes - Student
# ------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", centers=CENTERS)


@app.route("/start", methods=["POST"])
def start():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    center = request.form.get("center", "").strip()

    if not name or not email or not phone or not center:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("index"))

    user_id = generate_user_id()

    conn = get_db()
    conn.execute(
        "INSERT INTO users (user_id, name, email, phone, center) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, email, phone, center)
    )
    conn.commit()
    conn.close()

    session["user_id"] = user_id
    session["user_name"] = name
    session["user_email"] = email
    session["user_phone"] = phone
    session["user_center"] = center
    session["test_started_at"] = datetime.now().isoformat()
    return redirect(url_for("test"))    


@app.route("/test")
def test():
    if "user_id" not in session:
        return redirect(url_for("index"))
    questions = get_questions()
    return render_template(
        "test.html",
        questions=questions,
        user_name=session["user_name"],
        user_id=session["user_id"],
    )


@app.route("/submit", methods=["POST"])
def submit():
    if "user_id" not in session:
        return redirect(url_for("index"))

    questions = get_questions()
    answers = {}
    score = 0
    s1 = s2 = s3 = 0

    for q in questions:
        qid = str(q["question_number"])
        selected = request.form.get(f"q{qid}", "").upper()
        answers[qid] = selected
        if selected == q["correct_answer"]:
            score += 1
            if q["section"] == 1: s1 += 1
            elif q["section"] == 2: s2 += 1
            else: s3 += 1

    level, module = get_cefr_mapping(score)

    # Calculate time taken
    started_at = datetime.fromisoformat(session.get("test_started_at", datetime.now().isoformat()))
    completed_at = datetime.now()
    time_taken = int((completed_at - started_at).total_seconds())

    conn = get_db()
    conn.execute(
        """INSERT INTO attempts
           (user_id, user_name, user_email, user_phone, center,
            total_score, cefr_level, module_assigned,
            section1_score, section2_score, section3_score, answers,
            started_at, time_taken_seconds)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (session["user_id"], session["user_name"], session["user_email"],
         session["user_phone"], session["user_center"],
         score, level, module, s1, s2, s3, json.dumps(answers),
         started_at.isoformat(), time_taken)
    )
    conn.commit()
    conn.close()

    session.clear()
    # Don't show answers to student - just score and level
    return render_template(
        "results.html",
        score=score, total=len(questions),
        level=level, module=module,
        s1=s1, s2=s2, s3=s3,
    )


# ------------------------------------------------------------------
# Routes - Admin Auth
# ------------------------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = get_db()
        admin = conn.execute(
            "SELECT * FROM admins WHERE email=? AND password_hash=?",
            (email, hash_password(password))
        ).fetchone()
        conn.close()
        if admin:
            session["admin_email"] = email
            session["admin_name"] = admin["full_name"] or email
            flash("Logged in successfully.", "success")
            return redirect(url_for("admin"))
        else:
            flash("Invalid email or password.", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_email", None)
    session.pop("admin_name", None)
    return redirect(url_for("admin_login"))


@app.route("/admin/change-password", methods=["POST"])
def admin_change_password():
    if "admin_email" not in session:
        return redirect(url_for("admin_login"))
    current = request.form.get("current_password", "")
    new_pw = request.form.get("new_password", "")
    confirm = request.form.get("confirm_password", "")

    if new_pw != confirm:
        flash("New passwords do not match.", "error")
        return redirect(url_for("admin"))
    if len(new_pw) < 6:
        flash("Password must be at least 6 characters.", "error")
        return redirect(url_for("admin"))

    conn = get_db()
    admin = conn.execute(
        "SELECT * FROM admins WHERE email=? AND password_hash=?",
        (session["admin_email"], hash_password(current))
    ).fetchone()
    if not admin:
        flash("Current password is incorrect.", "error")
    else:
        conn.execute(
            "UPDATE admins SET password_hash=? WHERE email=?",
            (hash_password(new_pw), session["admin_email"])
        )
        conn.commit()
        flash("Password updated successfully.", "success")
    conn.close()
    return redirect(url_for("admin"))


# ------------------------------------------------------------------
# Routes - Admin Dashboard
# ------------------------------------------------------------------
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin_email" not in session:
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/admin")
@admin_required
def admin():
    filter_level = request.args.get("level", "")
    filter_center = request.args.get("center", "")
    filter_enrolled = request.args.get("enrolled", "")
    search = request.args.get("search", "").strip().lower()

    query = "SELECT * FROM attempts WHERE 1=1"
    params = []
    if filter_level:
        query += " AND cefr_level = ?"; params.append(filter_level)
    if filter_center:
        query += " AND center = ?"; params.append(filter_center)
    if filter_enrolled:
        query += " AND enrolled = ?"; params.append(int(filter_enrolled))
    if search:
        query += " AND (LOWER(user_name) LIKE ? OR LOWER(user_email) LIKE ? OR LOWER(user_phone) LIKE ? OR LOWER(user_id) LIKE ?)"
        params.extend([f"%{search}%"] * 4)

    query += " ORDER BY completed_at DESC"

    conn = get_db()
    attempts = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        "admin.html",
        attempts=[dict(a) for a in attempts],
        centers=CENTERS,
        filter_level=filter_level,
        filter_center=filter_center,
        filter_enrolled=filter_enrolled,
        search=search,
    )


@app.route("/admin/enroll/<int:attempt_id>", methods=["POST"])
@admin_required
def enroll_student(attempt_id):
    conn = get_db()
    conn.execute("UPDATE attempts SET enrolled = 1 WHERE id = ?", (attempt_id,))
    conn.commit()
    conn.close()
    flash("Student marked as enrolled.", "success")
    return redirect(url_for("admin"))


@app.route("/admin/view/<int:attempt_id>")
@admin_required
def view_attempt(attempt_id):
    conn = get_db()
    attempt = conn.execute("SELECT * FROM attempts WHERE id=?", (attempt_id,)).fetchone()
    questions = get_questions()
    conn.close()

    if not attempt:
        flash("Attempt not found.", "error")
        return redirect(url_for("admin"))

    answers = json.loads(attempt["answers"]) if attempt["answers"] else {}
    review = []
    for q in questions:
        qid = str(q["question_number"])
        user_ans = answers.get(qid, "-")
        review.append({
            "number": q["question_number"],
            "text": q["question_text"],
            "user_answer": user_ans,
            "correct_answer": q["correct_answer"],
            "is_correct": user_ans == q["correct_answer"],
        })

    return render_template(
        "admin_view.html",
        attempt=dict(attempt),
        review=review,
    )


@app.route("/admin/export")
@admin_required
def export_excel():
    conn = get_db()
    attempts = conn.execute("SELECT * FROM attempts ORDER BY completed_at DESC").fetchall()
    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "CEFR Results"

    headers = [
        "Date", "User ID", "Name", "Email", "Phone", "Center",
        "Total Score", "CEFR Level", "Module Assigned",
        "Section 1", "Section 2", "Section 3", "Time Taken", "Enrolled"
    ]
    ws.append(headers)

    for a in attempts:
        ws.append([
            a["completed_at"], a["user_id"], a["user_name"],
            a["user_email"], a["user_phone"], a["center"],
            a["total_score"], a["cefr_level"], a["module_assigned"],
            a["section1_score"], a["section2_score"], a["section3_score"],
            format_time_filter(a["time_taken_seconds"]),
            "Yes" if a["enrolled"] else "No",
        ])

    # Style header
    for cell in ws[1]:
        cell.font = cell.font.copy(bold=True)
        cell.fill = cell.fill.copy(start_color="667EEA")

    # Auto-width
    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max_len + 3

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"KG_CEFR_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename,
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)