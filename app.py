"""
StaffSync - Modern HR Management Solution
A Streamlit-based HR management system with role-based access for
HR Personnel, Employees, and Managers.

Deploy on Streamlit Cloud:
  1. Push this folder to a GitHub repo
  2. Go to share.streamlit.io
  3. Select the repo and set main file path to: app.py
  4. Click Deploy

Run locally:
  streamlit run app.py
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime

# Initialize database and auth on first load
import database as db
import auth
import components as ui

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="StaffSync - HR Management",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

ui.apply_custom_css()


# ---------- INIT ----------
@st.cache_resource
def init_app():
    """Initialize DB and seed demo data once."""
    db.init_db()
    auth.seed_demo_data()
    return True


init_app()


# ---------- SIDEBAR ----------
def render_sidebar():
    """Render the sidebar with user info and navigation."""
    with st.sidebar:
        st.markdown("### 👥 StaffSync")
        st.caption("Modern HR Management")

        if auth.is_authenticated():
            user = auth.get_current_user()
            st.markdown("---")
            st.markdown(f"**{user['full_name']}**")
            ui.render_role_badge(user["role"])
            if user.get("department"):
                st.caption(f"📍 {user['department']}")
            if user.get("position"):
                st.caption(f"💼 {user['position']}")
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                auth.logout_user()
                st.rerun()


# ---------- LOGIN PAGE ----------
def render_login_page():
    """Render the login / registration page."""
    ui.render_welcome_banner(
        "Welcome to StaffSync",
        "Modern Human Resource Management Solution"
    )

    st.markdown("""
    StaffSync streamlines and automates enterprise HR processes with role-based
    access for HR Personnel, Employees, and Managers. Manage employee data, approve
    leaves, track attendance, publish announcements, and coordinate training programs
    — all in one place.
    """)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    # ---- Login tab ----
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("#### Sign in to your account")
            username = st.text_input("Username", key="login_username", placeholder="e.g. hr_admin")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Sign In", type="primary", use_container_width=True):
                if username and password:
                    user = auth.authenticate(username, password)
                    if user:
                        auth.login_user(user)
                        st.success(f"Welcome back, {user['full_name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                else:
                    st.warning("Please enter both username and password.")

            st.markdown("---")
            st.markdown("**Demo Accounts** (password: `admin123`)")
            st.code("hr_admin    - HR Personnel\nmanager1    - Manager\nemployee1   - Employee", language="text")

    # ---- Register tab ----
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("#### Create a new employee account")
            with st.form("register_form"):
                full_name = st.text_input("Full Name *")
                email = st.text_input("Email *")
                username = st.text_input("Username *")
                password = st.text_input("Password *", type="password")
                col_a, col_b = st.columns(2)
                with col_a:
                    department = st.text_input("Department")
                with col_b:
                    position = st.text_input("Position")
                phone = st.text_input("Phone")
                join_date = st.date_input("Join Date", value=date.today())

                submitted = st.form_submit_button("Register", type="primary", use_container_width=True)
                if submitted:
                    if not all([full_name, email, username, password]):
                        st.error("Please fill in all required fields (*).")
                    else:
                        hashed = auth.hash_password(password)
                        ok, msg = db.create_user(
                            username=username,
                            password=hashed,
                            full_name=full_name,
                            email=email,
                            role="employee",
                            department=department,
                            position=position,
                            phone=phone,
                            join_date=join_date.isoformat(),
                        )
                        if ok:
                            st.success("Account created! Please switch to the Login tab.")
                        else:
                            st.error(msg)


# ---------- HR DASHBOARD ----------
def render_hr_dashboard():
    """Main HR Personnel dashboard."""
    user = auth.get_current_user()
    ui.render_welcome_banner(
        f"HR Portal - {user['full_name']}",
        "Manage employees, leaves, attendance, and announcements"
    )

    stats = db.get_hr_dashboard_stats()
    ui.render_metric_cards([
        ("Total Employees", stats["total_employees"]),
        ("Active", stats["active_employees"]),
        ("Present Today", stats["present_today"]),
        ("Pending Leaves", stats["pending_leaves"]),
    ])

    tab_emp, tab_leave, tab_att, tab_ann, tab_train = st.tabs([
        "👥 Employees", "📅 Leave Approvals", "✅ Attendance", "📢 Announcements", "🎓 Trainings"
    ])

    # ---- Employees tab ----
    with tab_emp:
        st.markdown("#### Employee Management")

        with st.expander("➕ Add New Employee"):
            with st.form("add_emp_form"):
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    e_name = st.text_input("Full Name *")
                    e_email = st.text_input("Email *")
                    e_username = st.text_input("Username *")
                    e_password = st.text_input("Password *", type="password", value="admin123")
                with e_col2:
                    e_dept = st.text_input("Department")
                    e_pos = st.text_input("Position")
                    e_phone = st.text_input("Phone")
                    e_role = st.selectbox("Role", ["employee", "manager", "hr"])
                managers = [u for u in db.get_all_users() if u["role"] == "manager"]
                mgr_options = {"None": None}
                for m in managers:
                    mgr_options[f"{m['full_name']} ({m['department']})"] = m["id"]
                e_mgr = st.selectbox("Reporting Manager", list(mgr_options.keys()))
                e_join = st.date_input("Join Date", value=date.today())

                if st.form_submit_button("Add Employee", type="primary"):
                    if not all([e_name, e_email, e_username, e_password]):
                        st.error("Please fill required fields (*).")
                    else:
                        hashed = auth.hash_password(e_password)
                        ok, msg = db.create_user(
                            username=e_username,
                            password=hashed,
                            full_name=e_name,
                            email=e_email,
                            role=e_role,
                            department=e_dept,
                            position=e_pos,
                            phone=e_phone,
                            join_date=e_join.isoformat(),
                            manager_id=mgr_options[e_mgr],
                        )
                        if ok:
                            st.success(f"Employee {e_name} added!")
                            st.rerun()
                        else:
                            st.error(msg)

        employees = db.get_all_employees()
        if employees:
            df = ui.format_df(employees, {
                "full_name": "Name",
                "email": "Email",
                "department": "Department",
                "position": "Position",
                "phone": "Phone",
                "manager_id": "Manager ID",
                "leave_balance": "Leave Balance",
                "status": "Status",
                "join_date": "Join Date",
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No employees yet. Add one above.")

    # ---- Leave Approvals tab ----
    with tab_leave:
        st.markdown("#### Leave Requests")
        filter_col1, filter_col2 = st.columns([1, 3])
        with filter_col1:
            status_filter = st.selectbox("Filter by Status", ["all", "pending", "approved", "rejected"])

        requests = db.get_all_leave_requests(status=None if status_filter == "all" else status_filter)
        if requests:
            for req in requests:
                ui.render_leave_request_row(req, show_reviewer_actions=True, reviewer_id=user["id"])
        else:
            st.info("No leave requests to display.")

    # ---- Attendance tab ----
    with tab_att:
        st.markdown("#### Today's Attendance")
        records = db.get_all_attendance_today()
        if records:
            df = ui.format_df(records, {
                "full_name": "Employee",
                "department": "Department",
                "date": "Date",
                "check_in": "Check-In",
                "check_out": "Check-Out",
                "work_hours": "Work Hours",
                "status": "Status",
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No attendance records for today yet.")

    # ---- Announcements tab ----
    with tab_ann:
        st.markdown("#### Announcements")

        with st.expander("➕ Publish New Announcement"):
            with st.form("ann_form"):
                a_title = st.text_input("Title *")
                a_content = st.text_area("Content *", height=120)
                a_audience = st.selectbox("Audience", ["all", "employee", "manager", "hr"])
                if st.form_submit_button("Publish", type="primary"):
                    if a_title and a_content:
                        db.create_announcement(a_title, a_content, a_audience, user["id"])
                        st.success("Announcement published!")
                        st.rerun()
                    else:
                        st.error("Please fill in title and content.")

        announcements = db.get_announcements()
        for ann in announcements:
            ui.render_announcement_card(ann)
            col_del, _ = st.columns([1, 5])
            with col_del:
                if st.button("🗑 Delete", key=f"del_ann_{ann['id']}"):
                    db.delete_announcement(ann["id"])
                    st.rerun()

    # ---- Trainings tab ----
    with tab_train:
        st.markdown("#### Training Programs")
        programs = db.get_all_training_programs()
        if programs:
            df = ui.format_df(programs, {
                "title": "Program",
                "department": "Department",
                "trainer": "Trainer",
                "start_date": "Start",
                "end_date": "End",
                "duration_hours": "Hours",
                "capacity": "Capacity",
                "enrolled_count": "Enrolled",
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No training programs yet.")


# ---------- EMPLOYEE DASHBOARD ----------
def render_employee_dashboard():
    """Main Employee dashboard."""
    user = auth.get_current_user()
    ui.render_welcome_banner(
        f"Hello, {user['full_name'].split()[0]}!",
        f"{user.get('position', 'Employee')} • {user.get('department', 'General')}"
    )

    today_att = db.get_today_attendance(user["id"])
    pending_leaves = [l for l in db.get_leave_requests_by_user(user["id"]) if l["status"] == "pending"]
    announcements = db.get_announcements(audience=user["role"])

    ui.render_metric_cards([
        ("Leave Balance", f"{user.get('leave_balance', 0)} days"),
        ("Checked In", "Yes ✓" if (today_att and today_att["check_in"]) else "No"),
        ("Pending Leaves", len(pending_leaves)),
        ("Announcements", len(announcements)),
    ])

    tab_dash, tab_leave, tab_att, tab_ann, tab_train, tab_profile = st.tabs([
        "🏠 Overview", "📅 My Leaves", "⏰ Attendance", "📢 Announcements", "🎓 Trainings", "👤 Profile"
    ])

    # ---- Overview tab ----
    with tab_dash:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### ⏰ Quick Attendance")
            if today_att and today_att["check_in"] and not today_att["check_out"]:
                st.info(f"Checked in at **{today_att['check_in']}**")
                if st.button("Check Out", type="primary", use_container_width=True):
                    ok, msg = db.check_out(user["id"])
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            elif today_att and today_att["check_out"]:
                st.success(f"Day complete! In: {today_att['check_in']} → Out: {today_att['check_out']} ({today_att['work_hours']}h)")
            else:
                st.warning("You haven't checked in today.")
                if st.button("Check In", type="primary", use_container_width=True):
                    ok, msg = db.check_in(user["id"])
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with col2:
            st.markdown("##### 📢 Latest Announcement")
            if announcements:
                ann = announcements[0]
                ui.render_announcement_card(ann)
            else:
                st.info("No announcements yet.")

    # ---- Leave tab ----
    with tab_leave:
        st.markdown("#### Apply for Leave")
        with st.expander("➕ New Leave Request"):
            with st.form("leave_form"):
                l_col1, l_col2 = st.columns(2)
                with l_col1:
                    l_type = st.selectbox("Leave Type", ["Annual", "Sick", "Personal", "Unpaid", "Maternity/Paternity"])
                    l_start = st.date_input("Start Date", min_value=date.today())
                with l_col2:
                    l_end = st.date_input("End Date", min_value=l_start)
                    l_reason = st.text_area("Reason")
                if l_end < l_start:
                    st.error("End date must be after start date.")
                days = ui.calculate_leave_days(l_start.isoformat(), l_end.isoformat()) if l_end >= l_start else 0
                st.caption(f"Total days: **{days}**")
                if st.form_submit_button("Submit Request", type="primary"):
                    if days > 0:
                        db.create_leave_request(user["id"], l_type, l_start.isoformat(), l_end.isoformat(), days, l_reason)
                        st.success("Leave request submitted!")
                        st.rerun()
                    else:
                        st.error("Invalid date range.")

        st.markdown("#### My Leave History")
        requests = db.get_leave_requests_by_user(user["id"])
        if requests:
            df = ui.format_df(requests, {
                "leave_type": "Type",
                "start_date": "Start",
                "end_date": "End",
                "days": "Days",
                "status": "Status",
                "applied_at": "Applied",
                "review_comment": "Reviewer Comment",
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("You haven't applied for any leaves yet.")

    # ---- Attendance tab ----
    with tab_att:
        st.markdown("#### My Attendance")
        today_att = db.get_today_attendance(user["id"])
        if today_att and today_att["check_in"] and not today_att["check_out"]:
            st.info(f"Checked in at **{today_att['check_in']}** — don't forget to check out!")
            if st.button("Check Out Now", type="primary"):
                ok, msg = db.check_out(user["id"])
                if ok:
                    st.success(msg)
                    st.rerun()
        elif today_att and today_att["check_out"]:
            st.success(f"Today: In {today_att['check_in']} → Out {today_att['check_out']} ({today_att['work_hours']}h)")
        else:
            if st.button("Check In Now", type="primary"):
                ok, msg = db.check_in(user["id"])
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("##### Recent History")
        history = db.get_attendance_history(user["id"])
        if history:
            df = ui.format_df(history, {
                "date": "Date",
                "check_in": "Check-In",
                "check_out": "Check-Out",
                "work_hours": "Hours",
                "status": "Status",
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No attendance history yet.")

    # ---- Announcements tab ----
    with tab_ann:
        st.markdown("#### Company Announcements")
        announcements = db.get_announcements(audience=user["role"])
        if announcements:
            for ann in announcements:
                ui.render_announcement_card(ann)
        else:
            st.info("No announcements available.")

    # ---- Trainings tab ----
    with tab_train:
        st.markdown("#### Available Training Programs")
        programs = db.get_all_training_programs()
        my_enrollments = db.get_user_enrollments(user["id"])
        enrolled_ids = {p["id"] for p in my_enrollments}

        if programs:
            for p in programs:
                with st.container():
                    col1, col2, col3 = st.columns([4, 2, 1])
                    with col1:
                        st.markdown(f"**{p['title']}**")
                        st.caption(p["description"] or "")
                        st.caption(f"Trainer: {p['trainer']} | {p['start_date']} → {p['end_date']} | {p['duration_hours']}h")
                    with col2:
                        st.metric("Enrolled", f"{p['enrolled_count']}/{p['capacity']}")
                    with col3:
                        if p["id"] in enrolled_ids:
                            st.success("✓ Enrolled")
                        else:
                            if st.button("Enroll", key=f"enroll_{p['id']}"):
                                ok, msg = db.enroll_in_training(p["id"], user["id"])
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.info(msg)
                    st.divider()
        else:
            st.info("No training programs available.")

        st.markdown("##### My Enrolled Programs")
        if my_enrollments:
            df = ui.format_df(my_enrollments, {
                "title": "Program",
                "department": "Department",
                "trainer": "Trainer",
                "start_date": "Start",
                "end_date": "End",
                "enrolled_at": "Enrolled On",
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("You haven't enrolled in any programs.")

    # ---- Profile tab ----
    with tab_profile:
        st.markdown("#### My Profile")
        with st.form("profile_form"):
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                p_name = st.text_input("Full Name", value=user["full_name"])
                p_email = st.text_input("Email", value=user["email"])
                p_dept = st.text_input("Department", value=user.get("department", ""))
            with p_col2:
                p_pos = st.text_input("Position", value=user.get("position", ""))
                p_phone = st.text_input("Phone", value=user.get("phone", ""))
                st.text_input("Username", value=user["username"], disabled=True)

            if st.form_submit_button("Update Profile", type="primary"):
                db.update_user(user["id"], p_name, p_email, p_dept, p_pos, p_phone)
                # Refresh session
                updated = db.get_user_by_id(user["id"])
                auth.login_user(updated)
                st.success("Profile updated!")
                st.rerun()


# ---------- MANAGER DASHBOARD ----------
def render_manager_dashboard():
    """Main Manager dashboard."""
    user = auth.get_current_user()
    ui.render_welcome_banner(
        f"Manager Portal - {user['full_name']}",
        f"{user.get('department', 'Team')} • Team Leadership"
    )

    stats = db.get_manager_dashboard_stats(user["id"])
    ui.render_metric_cards([
        ("Team Size", stats["team_size"]),
        ("Pending Leaves", stats["pending_leaves"]),
        ("My Trainings", stats["my_trainings"]),
    ])

    tab_team, tab_leave, tab_train = st.tabs(["👥 My Team", "📅 Leave Review", "🎓 Training Programs"])

    # ---- Team tab ----
    with tab_team:
        st.markdown("#### Team Members")
        team = db.get_team_members(user["id"])
        if team:
            df = ui.format_df(team, {
                "full_name": "Name",
                "email": "Email",
                "position": "Position",
                "phone": "Phone",
                "leave_balance": "Leave Balance",
                "status": "Status",
                "join_date": "Join Date",
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No team members assigned to you. Contact HR to assign employees.")

    # ---- Leave Review tab ----
    with tab_leave:
        st.markdown("#### Team Leave Requests")
        filter_col1, _ = st.columns([1, 3])
        with filter_col1:
            status_filter = st.selectbox("Filter", ["all", "pending", "approved", "rejected"], key="mgr_leave_filter")

        requests = db.get_team_leave_requests(
            user["id"],
            status=None if status_filter == "all" else status_filter
        )
        if requests:
            for req in requests:
                ui.render_leave_request_row(req, show_reviewer_actions=True, reviewer_id=user["id"])
        else:
            st.info("No leave requests from your team.")

    # ---- Training tab ----
    with tab_train:
        st.markdown("#### Training & Development Programs")

        with st.expander("➕ Create New Training Program"):
            with st.form("train_form"):
                t_col1, t_col2 = st.columns(2)
                with t_col1:
                    t_title = st.text_input("Program Title *")
                    t_trainer = st.text_input("Trainer *", value=user["full_name"])
                    t_dept = st.text_input("Target Department", value=user.get("department", ""))
                with t_col2:
                    t_start = st.date_input("Start Date", min_value=date.today())
                    t_end = st.date_input("End Date", min_value=t_start)
                    t_hours = st.number_input("Duration (hours)", min_value=1, value=8)
                    t_cap = st.number_input("Capacity", min_value=1, value=20)
                t_desc = st.text_area("Description")

                if st.form_submit_button("Create Program", type="primary"):
                    if t_title and t_trainer:
                        db.create_training_program(
                            t_title, t_desc, t_dept, t_trainer,
                            t_start.isoformat(), t_end.isoformat(), t_hours, t_cap, user["id"]
                        )
                        st.success("Training program created!")
                        st.rerun()
                    else:
                        st.error("Please fill required fields (*).")

        st.markdown("##### All Programs")
        programs = db.get_all_training_programs()
        if programs:
            for p in programs:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{p['title']}**")
                        st.caption(p["description"] or "")
                        st.caption(f"Trainer: {p['trainer']} | {p['department']} | {p['start_date']} → {p['end_date']} | {p['duration_hours']}h")
                    with col2:
                        st.metric("Enrolled", f"{p['enrolled_count']}/{p['capacity']}")
                        if p["created_by"] == user["id"]:
                            if st.button("🗑 Delete", key=f"del_train_{p['id']}"):
                                db.delete_training_program(p["id"])
                                st.rerun()
                    st.divider()
        else:
            st.info("No training programs yet. Create one above.")


# ---------- MAIN ROUTER ----------
def main():
    render_sidebar()

    if not auth.is_authenticated():
        render_login_page()
        return

    user = auth.get_current_user()
    role = user["role"]

    if role == "hr":
        render_hr_dashboard()
    elif role == "manager":
        render_manager_dashboard()
    elif role == "employee":
        render_employee_dashboard()
    else:
        st.error("Unknown role. Contact HR.")


if __name__ == "__main__":
    main()
