"""
StaffSync UI Components
Reusable UI elements and styling for the HR Management System.
"""
import streamlit as st
import pandas as pd
from datetime import datetime


ROLE_LABELS = {
    "hr": "HR Personnel",
    "employee": "Employee",
    "manager": "Manager",
}

ROLE_COLORS = {
    "hr": "#DC2626",
    "employee": "#059669",
    "manager": "#4F46E5",
}

ROLE_ICONS = {
    "hr": "🏢",
    "employee": "👤",
    "manager": "👔",
}


def apply_custom_css():
    """Inject custom CSS styling."""
    st.markdown("""
    <style>
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #F0F4FF 0%, #FFFFFF 100%);
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E5E7EB;
        padding: 18px 20px;
        border-radius: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    div[data-testid="stMetric"] label {
        color: #6B7280;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #111827;
        font-size: 1.7rem;
        font-weight: 700;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E1B4B 0%, #312E81 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #E0E7FF !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stTextInput label {
        color: #C7D2FE !important;
    }

    /* Cards / info boxes */
    .info-card {
        background: white;
        padding: 20px;
        border-radius: 14px;
        border-left: 4px solid #4F46E5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        margin-bottom: 12px;
    }

    .status-badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-pending { background: #FEF3C7; color: #92400E; }
    .status-approved { background: #D1FAE5; color: #065F46; }
    .status-rejected { background: #FEE2E2; color: #991B1B; }

    /* Headers */
    h1, h2, h3 {
        color: #1F2937 !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }

    /* DataFrame / tables */
    .stDataFrame, .stTable {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Welcome banner */
    .welcome-banner {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        padding: 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
    }
    .welcome-banner h1 {
        color: white !important;
        margin: 0 0 8px 0;
        font-size: 1.8rem;
    }
    .welcome-banner p {
        color: #E0E7FF;
        margin: 0;
        font-size: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


def render_welcome_banner(title, subtitle):
    """Render a gradient welcome banner."""
    st.markdown(f"""
    <div class="welcome-banner">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_role_badge(role):
    """Render a colored role badge."""
    label = ROLE_LABELS.get(role, role.title())
    color = ROLE_COLORS.get(role, "#6B7280")
    icon = ROLE_ICONS.get(role, "")
    st.markdown(f"""
    <span style="
        display:inline-block;
        padding: 4px 14px;
        background: {color}22;
        color: {color};
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid {color}44;
    ">{icon} {label}</span>
    """, unsafe_allow_html=True)


def render_status_badge(status):
    """Render a status badge (pending/approved/rejected)."""
    css_class = f"status-{status}" if status in ("pending", "approved", "rejected") else ""
    st.markdown(f'<span class="status-badge {css_class}">{status.title()}</span>', unsafe_allow_html=True)


def render_metric_cards(metrics):
    """Render a row of metric cards.
    metrics: list of (label, value) tuples.
    """
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)


def render_announcement_card(ann):
    """Render an announcement as a card."""
    publisher = ann["publisher_name"] or "System"
    published = ann["published_at"][:16] if ann["published_at"] else ""
    st.markdown(f"""
    <div class="info-card">
        <h3 style="margin:0 0 8px 0; color:#1F2937;">{ann['title']}</h3>
        <p style="color:#4B5563; margin:0 0 10px 0;">{ann['content']}</p>
        <p style="color:#9CA3AF; font-size:0.8rem; margin:0;">
            <strong>{publisher}</strong> • {published} • Audience: {ann['audience']}
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_leave_request_row(req, show_reviewer_actions=False, reviewer_id=None):
    """Render a leave request entry."""
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        with col1:
            st.markdown(f"**{req['applicant_name']}**" if "applicant_name" in req.keys() else f"**Leave #{req['id']}**")
            st.caption(f"{req['leave_type']} • {req['days']} day(s)")
            if req.get("reason"):
                st.caption(f"Reason: {req['reason']}")
        with col2:
            st.caption("Period")
            st.write(f"{req['start_date']} → {req['end_date']}")
        with col3:
            st.caption("Status")
            render_status_badge(req["status"])
        with col4:
            st.caption("Applied")
            st.write((req["applied_at"] or "")[:10])

        if show_reviewer_actions and req["status"] == "pending":
            rcol1, rcol2, rcol3 = st.columns([1, 1, 3])
            with rcol1:
                if st.button("Approve", key=f"approve_{req['id']}", type="primary"):
                    db.review_leave_request(req["id"], "approved", reviewer_id)
                    st.success("Leave approved!")
                    st.rerun()
            with rcol2:
                if st.button("Reject", key=f"reject_{req['id']}"):
                    db.review_leave_request(req["id"], "rejected", reviewer_id)
                    st.error("Leave rejected.")
                    st.rerun()

        st.divider()


def format_df(rows, columns_map):
    """Convert sqlite Rows to a pretty DataFrame.
    columns_map: dict mapping db keys -> display labels.
    """
    data = []
    for row in rows:
        item = {}
        for key, label in columns_map.items():
            item[label] = row[key] if key in row.keys() else ""
        data.append(item)
    return pd.DataFrame(data)


def calculate_leave_days(start_date, end_date):
    """Calculate number of days between two dates (inclusive)."""
    from datetime import datetime
    d1 = datetime.strptime(start_date, "%Y-%m-%d")
    d2 = datetime.strptime(end_date, "%Y-%m-%d")
    return (d2 - d1).days + 1


# Import db here to avoid circular imports at module level
import database as db
