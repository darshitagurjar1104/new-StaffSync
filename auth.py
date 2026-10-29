"""
StaffSync Authentication Module
Handles user authentication, password hashing, and session management.
"""
import streamlit as st
import bcrypt
import database as db


def hash_password(password):
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password, hashed):
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def authenticate(username, password):
    """Authenticate a user. Returns user dict if valid, None otherwise."""
    user = db.get_user_by_username(username)
    if user and verify_password(password, user["password"]):
        return user
    return None


def login_user(user):
    """Store user info in session state."""
    st.session_state["user"] = dict(user)
    st.session_state["authenticated"] = True


def logout_user():
    """Clear session state."""
    keys_to_clear = ["user", "authenticated"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def is_authenticated():
    """Check if user is authenticated."""
    return st.session_state.get("authenticated", False)


def get_current_user():
    """Get the current logged-in user dict."""
    return st.session_state.get("user", None)


def require_role(*roles):
    """Check if current user has one of the required roles."""
    user = get_current_user()
    if not user:
        return False
    return user.get("role") in roles


def seed_demo_data():
    """Create demo accounts on first run if no users exist."""
    users = db.get_all_users()
    if users:
        return False

    # HR admin
    db.create_user(
        username="hr_admin",
        password=hash_password("admin123"),
        full_name="Sarah Johnson",
        email="sarah.johnson@staffsync.com",
        role="hr",
        department="Human Resources",
        position="HR Director",
        phone="+1-555-0101",
    )

    # Manager
    db.create_user(
        username="manager1",
        password=hash_password("admin123"),
        full_name="Michael Chen",
        email="michael.chen@staffsync.com",
        role="manager",
        department="Engineering",
        position="Engineering Manager",
        phone="+1-555-0102",
    )

    manager = db.get_user_by_username("manager1")

    # Employees
    employees = [
        ("employee1", "Emily Davis", "emily.davis@staffsync.com", "Engineering", "Software Engineer", "+1-555-0103"),
        ("employee2", "James Wilson", "james.wilson@staffsync.com", "Engineering", "Senior Developer", "+1-555-0104"),
        ("employee3", "Olivia Brown", "olivia.brown@staffsync.com", "Marketing", "Marketing Specialist", "+1-555-0105"),
        ("employee4", "Daniel Martinez", "daniel.martinez@staffsync.com", "Sales", "Sales Representative", "+1-555-0106"),
    ]

    for username, name, email, dept, position, phone in employees:
        db.create_user(
            username=username,
            password=hash_password("admin123"),
            full_name=name,
            email=email,
            role="employee",
            department=dept,
            position=position,
            phone=phone,
            manager_id=manager["id"] if dept == "Engineering" else None,
        )

    # Sample announcement
    hr_user = db.get_user_by_username("hr_admin")
    db.create_announcement(
        title="Welcome to StaffSync!",
        content="Welcome to StaffSync, our new HR management platform. Please update your profile and explore the features. For any issues, contact HR.",
        audience="all",
        published_by=hr_user["id"],
    )

    db.create_announcement(
        title="Quarterly Team Meeting",
        content="The quarterly all-hands meeting is scheduled for next Friday at 10 AM in the main conference room. Attendance is mandatory.",
        audience="all",
        published_by=hr_user["id"],
    )

    # Sample training program
    db.create_training_program(
        title="React Best Practices Workshop",
        description="A hands-on workshop covering modern React patterns, hooks, state management, and performance optimization techniques.",
        department="Engineering",
        trainer="Michael Chen",
        start_date="2026-11-15",
        end_date="2026-11-16",
        duration_hours=8,
        capacity=20,
        created_by=manager["id"],
    )

    db.create_training_program(
        title="Leadership & Communication Skills",
        description="Develop essential leadership and communication skills to advance your career. Open to all departments.",
        department="All",
        trainer="Sarah Johnson",
        start_date="2026-11-20",
        end_date="2026-11-22",
        duration_hours=12,
        capacity=30,
        created_by=manager["id"],
    )

    return True
