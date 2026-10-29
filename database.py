"""
StaffSync Database Module
Handles all SQLite database operations for the HR Management System.
"""
import sqlite3
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "staffsync.db")


def get_connection():
    """Create and return a database connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize the database with all required tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users / Employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('hr', 'employee', 'manager')),
            department TEXT,
            position TEXT,
            phone TEXT,
            join_date TEXT,
            manager_id INTEGER,
            leave_balance INTEGER DEFAULT 24,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (manager_id) REFERENCES users(id)
        )
    """)

    # Leave requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            days INTEGER NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
            reviewed_by INTEGER,
            reviewed_at TEXT,
            review_comment TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (reviewed_by) REFERENCES users(id)
        )
    """)

    # Attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            check_in TEXT,
            check_out TEXT,
            work_hours REAL DEFAULT 0,
            status TEXT DEFAULT 'present',
            UNIQUE(user_id, date),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Announcements table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            audience TEXT DEFAULT 'all',
            published_by INTEGER,
            published_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (published_by) REFERENCES users(id)
        )
    """)

    # Training programs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            department TEXT,
            trainer TEXT,
            start_date TEXT,
            end_date TEXT,
            duration_hours INTEGER,
            capacity INTEGER,
            created_by INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    # Training enrollments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            enrolled_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'enrolled',
            UNIQUE(program_id, user_id),
            FOREIGN KEY (program_id) REFERENCES training_programs(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ==================== USER OPERATIONS ====================

def create_user(username, password, full_name, email, role, department="", position="", phone="", join_date=None, manager_id=None):
    """Insert a new user. Returns (success, message)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password, full_name, email, role, department, position, phone, join_date, manager_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, password, full_name, email, role, department, position, phone,
              join_date or date.today().isoformat(), manager_id))
        conn.commit()
        return True, "User created successfully."
    except sqlite3.IntegrityError as e:
        return False, f"Username already exists. {e}"
    finally:
        conn.close()


def get_user_by_username(username):
    """Fetch a user by username."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    """Fetch a user by id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_all_employees():
    """Fetch all users with role 'employee'."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE role = 'employee' ORDER BY full_name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_users():
    """Fetch all users."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY full_name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_team_members(manager_id):
    """Fetch all employees reporting to a manager."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE manager_id = ? ORDER BY full_name", (manager_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_user(user_id, full_name, email, department, position, phone):
    """Update user profile fields."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET full_name=?, email=?, department=?, position=?, phone=?
        WHERE id=?
    """, (full_name, email, department, position, phone, user_id))
    conn.commit()
    conn.close()


def update_leave_balance(user_id, delta):
    """Adjust a user's leave balance."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET leave_balance = leave_balance + ? WHERE id = ?", (delta, user_id))
    conn.commit()
    conn.close()


def delete_user(user_id):
    """Delete a user account."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


# ==================== LEAVE OPERATIONS ====================

def create_leave_request(user_id, leave_type, start_date, end_date, days, reason):
    """Create a new leave request."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leave_requests (user_id, leave_type, start_date, end_date, days, reason)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, leave_type, start_date, end_date, days, reason))
    conn.commit()
    conn.close()


def get_leave_requests_by_user(user_id):
    """Fetch leave requests for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT lr.*, u.full_name as applicant_name, r.full_name as reviewer_name
        FROM leave_requests lr
        JOIN users u ON lr.user_id = u.id
        LEFT JOIN users r ON lr.reviewed_by = r.id
        WHERE lr.user_id = ?
        ORDER BY lr.applied_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_leave_requests(status=None):
    """Fetch all leave requests, optionally filtered by status."""
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("""
            SELECT lr.*, u.full_name as applicant_name, u.department, r.full_name as reviewer_name
            FROM leave_requests lr
            JOIN users u ON lr.user_id = u.id
            LEFT JOIN users r ON lr.reviewed_by = r.id
            WHERE lr.status = ?
            ORDER BY lr.applied_at DESC
        """, (status,))
    else:
        cursor.execute("""
            SELECT lr.*, u.full_name as applicant_name, u.department, r.full_name as reviewer_name
            FROM leave_requests lr
            JOIN users u ON lr.user_id = u.id
            LEFT JOIN users r ON lr.reviewed_by = r.id
            ORDER BY lr.applied_at DESC
        """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_team_leave_requests(manager_id, status=None):
    """Fetch leave requests for team members of a manager."""
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("""
            SELECT lr.*, u.full_name as applicant_name, u.department, r.full_name as reviewer_name
            FROM leave_requests lr
            JOIN users u ON lr.user_id = u.id
            LEFT JOIN users r ON lr.reviewed_by = r.id
            WHERE u.manager_id = ? AND lr.status = ?
            ORDER BY lr.applied_at DESC
        """, (manager_id, status))
    else:
        cursor.execute("""
            SELECT lr.*, u.full_name as applicant_name, u.department, r.full_name as reviewer_name
            FROM leave_requests lr
            JOIN users u ON lr.user_id = u.id
            LEFT JOIN users r ON lr.reviewed_by = r.id
            WHERE u.manager_id = ?
            ORDER BY lr.applied_at DESC
        """, (manager_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def review_leave_request(request_id, status, reviewer_id, comment=""):
    """Approve or reject a leave request. Adjusts leave balance if approved."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE leave_requests
        SET status=?, reviewed_by=?, reviewed_at=CURRENT_TIMESTAMP, review_comment=?
        WHERE id=?
    """, (status, reviewer_id, comment, request_id))

    # If approved, deduct leave balance
    if status == "approved":
        cursor.execute("SELECT user_id, days FROM leave_requests WHERE id = ?", (request_id,))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE users SET leave_balance = leave_balance - ? WHERE id = ?", (row["days"], row["user_id"]))

    conn.commit()
    conn.close()


# ==================== ATTENDANCE OPERATIONS ====================

def check_in(user_id):
    """Record check-in for today."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    now = datetime.now().strftime("%H:%M:%S")
    try:
        cursor.execute("""
            INSERT INTO attendance (user_id, date, check_in, status)
            VALUES (?, ?, ?, 'present')
        """, (user_id, today, now))
        conn.commit()
        return True, f"Checked in at {now}"
    except sqlite3.IntegrityError:
        return False, "Already checked in today."
    finally:
        conn.close()


def check_out(user_id):
    """Record check-out for today."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    now = datetime.now().strftime("%H:%M:%S")

    cursor.execute("SELECT check_in FROM attendance WHERE user_id = ? AND date = ?", (user_id, today))
    row = cursor.fetchone()
    if not row or not row["check_in"]:
        conn.close()
        return False, "You haven't checked in today."

    if row["check_in"]:
        fmt = "%H:%M:%S"
        t1 = datetime.strptime(row["check_in"], fmt)
        t2 = datetime.strptime(now, fmt)
        hours = round((t2 - t1).total_seconds() / 3600, 2)
    else:
        hours = 0

    cursor.execute("""
        UPDATE attendance SET check_out=?, work_hours=? WHERE user_id=? AND date=?
    """, (now, hours, user_id, today))
    conn.commit()
    conn.close()
    return True, f"Checked out at {now}. Work hours: {hours}"


def get_today_attendance(user_id):
    """Get today's attendance record for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("SELECT * FROM attendance WHERE user_id = ? AND date = ?", (user_id, today))
    row = cursor.fetchone()
    conn.close()
    return row


def get_attendance_history(user_id, limit=30):
    """Get attendance history for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM attendance WHERE user_id = ? ORDER BY date DESC LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_attendance_today():
    """Get today's attendance for all employees."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("""
        SELECT a.*, u.full_name, u.department
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        WHERE a.date = ?
        ORDER BY u.full_name
    """, (today,))
    rows = cursor.fetchall()
    conn.close()
    return rows


# ==================== ANNOUNCEMENT OPERATIONS ====================

def create_announcement(title, content, audience, published_by):
    """Create a new announcement."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO announcements (title, content, audience, published_by)
        VALUES (?, ?, ?, ?)
    """, (title, content, audience, published_by))
    conn.commit()
    conn.close()


def get_announcements(audience=None):
    """Fetch announcements, optionally filtered by audience."""
    conn = get_connection()
    cursor = conn.cursor()
    if audience and audience != "all":
        cursor.execute("""
            SELECT a.*, u.full_name as publisher_name
            FROM announcements a
            LEFT JOIN users u ON a.published_by = u.id
            WHERE a.audience IN ('all', ?)
            ORDER BY a.published_at DESC
        """, (audience,))
    else:
        cursor.execute("""
            SELECT a.*, u.full_name as publisher_name
            FROM announcements a
            LEFT JOIN users u ON a.published_by = u.id
            ORDER BY a.published_at DESC
        """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_announcement(ann_id):
    """Delete an announcement."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM announcements WHERE id = ?", (ann_id,))
    conn.commit()
    conn.close()


# ==================== TRAINING OPERATIONS ====================

def create_training_program(title, description, department, trainer, start_date, end_date, duration_hours, capacity, created_by):
    """Create a new training program."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO training_programs (title, description, department, trainer, start_date, end_date, duration_hours, capacity, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, description, department, trainer, start_date, end_date, duration_hours, capacity, created_by))
    conn.commit()
    conn.close()


def get_all_training_programs():
    """Fetch all training programs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tp.*, COUNT(te.id) as enrolled_count
        FROM training_programs tp
        LEFT JOIN training_enrollments te ON tp.id = te.program_id
        GROUP BY tp.id
        ORDER BY tp.start_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def enroll_in_training(program_id, user_id):
    """Enroll a user in a training program."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO training_enrollments (program_id, user_id)
            VALUES (?, ?)
        """, (program_id, user_id))
        conn.commit()
        return True, "Enrolled successfully."
    except sqlite3.IntegrityError:
        return False, "Already enrolled."
    finally:
        conn.close()


def get_user_enrollments(user_id):
    """Fetch training programs a user is enrolled in."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tp.*, te.enrolled_at
        FROM training_enrollments te
        JOIN training_programs tp ON te.program_id = tp.id
        WHERE te.user_id = ?
        ORDER BY te.enrolled_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_training_program(program_id):
    """Delete a training program."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM training_enrollments WHERE program_id = ?", (program_id,))
    cursor.execute("DELETE FROM training_programs WHERE id = ?", (program_id,))
    conn.commit()
    conn.close()


# ==================== DASHBOARD STATS ====================

def get_hr_dashboard_stats():
    """Get aggregate stats for the HR dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    stats = {}

    cursor.execute("SELECT COUNT(*) as c FROM users WHERE role = 'employee'")
    stats["total_employees"] = cursor.fetchone()["c"]

    cursor.execute("SELECT COUNT(*) as c FROM users WHERE role = 'employee' AND status = 'active'")
    stats["active_employees"] = cursor.fetchone()["c"]

    cursor.execute("SELECT COUNT(*) as c FROM leave_requests WHERE status = 'pending'")
    stats["pending_leaves"] = cursor.fetchone()["c"]

    today = date.today().isoformat()
    cursor.execute("SELECT COUNT(*) as c FROM attendance WHERE date = ? AND status = 'present'", (today,))
    stats["present_today"] = cursor.fetchone()["c"]

    cursor.execute("SELECT COUNT(*) as c FROM announcements")
    stats["total_announcements"] = cursor.fetchone()["c"]

    cursor.execute("SELECT COUNT(*) as c FROM training_programs")
    stats["total_trainings"] = cursor.fetchone()["c"]

    conn.close()
    return stats


def get_manager_dashboard_stats(manager_id):
    """Get aggregate stats for a manager's dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    stats = {}

    cursor.execute("SELECT COUNT(*) as c FROM users WHERE manager_id = ?", (manager_id,))
    stats["team_size"] = cursor.fetchone()["c"]

    cursor.execute("SELECT COUNT(*) as c FROM leave_requests lr JOIN users u ON lr.user_id = u.id WHERE u.manager_id = ? AND lr.status = 'pending'", (manager_id,))
    stats["pending_leaves"] = cursor.fetchone()["c"]

    cursor.execute("SELECT COUNT(*) as c FROM training_programs WHERE created_by = ?", (manager_id,))
    stats["my_trainings"] = cursor.fetchone()["c"]

    conn.close()
    return stats
