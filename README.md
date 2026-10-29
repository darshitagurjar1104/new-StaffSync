# 👥 StaffSync — Modern HR Management Solution

A comprehensive **Streamlit-based** Human Resource Management System with role-based access for **HR Personnel**, **Employees**, and **Managers**. Built to streamline and automate enterprise HR processes — manage employee data, approve leaves, track attendance, publish announcements, and coordinate training programs, all in one place.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

### 🏢 HR Personnel
- **Employee Management** — add, view, and manage all employee records
- **Leave Approvals** — review and approve/reject leave requests across the company
- **Attendance Tracking** — view today's attendance for all employees
- **Announcements** — publish company-wide or role-targeted announcements
- **Training Overview** — view all training programs

### 👤 Employee
- **Apply for Leave** — submit leave requests with type, dates, and reason
- **Attendance Check-in/Check-out** — daily attendance with automatic work-hour calculation
- **View Announcements** — see company announcements targeted to your role
- **Training Enrollment** — browse and enroll in available training programs
- **Profile Management** — update personal information

### 👔 Manager
- **Team Overview** — view all team members reporting to you
- **Leave Review** — approve/reject leave requests from your team
- **Training Programs** — create and manage training & development programs for your team

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.9 or higher
- pip

### Installation

```bash
# 1. Navigate to the project folder
cd staffsync

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### Demo Accounts

The app auto-creates demo accounts on first run (password for all: `admin123`):

| Username     | Role           | Name            |
|--------------|----------------|-----------------|
| `hr_admin`   | HR Personnel   | Sarah Johnson   |
| `manager1`   | Manager        | Michael Chen    |
| `employee1`  | Employee       | Emily Davis     |
| `employee2`  | Employee       | James Wilson    |
| `employee3`  | Employee       | Olivia Brown    |
| `employee4`  | Employee       | Daniel Martinez |

You can also register new employee accounts from the login page.

---

## ☁️ Deploy on Streamlit Cloud (Free)

Streamlit Cloud offers free hosting for public Streamlit apps. Here's how to deploy:

### Step 1: Push to GitHub

1. Create a new repository on [GitHub](https://github.com/new) (e.g., `staffsync`)
2. Push all files in the `staffsync/` folder to the repo:

```bash
cd staffsync
git init
git add .
git commit -m "Initial commit: StaffSync HR Management System"
git branch -M main
git remote add origin https://github.com/<your-username>/staffsync.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in:
   - **Repository**: `<your-username>/staffsync`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click **"Deploy!"**

Your app will be live at `https://<your-app-name>.streamlit.app` within 2–5 minutes.

### Notes for Streamlit Cloud
- The SQLite database (`data/staffsync.db`) is created automatically on first run in the app's working directory.
- For persistent data across redeployments, consider connecting an external database (PostgreSQL on Supabase, MongoDB Atlas, etc.). The `database.py` module can be adapted to use any DB.
- Demo data is seeded automatically on first run if the database is empty.

---

## 📁 Project Structure

```
staffsync/
├── app.py                 # Main application (entry point)
├── database.py            # SQLite database operations
├── auth.py                # Authentication & password hashing
├── components.py          # Reusable UI components & styling
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── .streamlit/
│   └── config.toml        # Streamlit theme & server config
└── data/                  # Auto-created: SQLite database storage
    └── staffsync.db       # Auto-created on first run
```

---

## 🛠 Technology Stack

| Component       | Technology              |
|-----------------|-------------------------|
| Framework       | Streamlit (Python)      |
| Database        | SQLite                  |
| Authentication  | bcrypt (password hashing)|
| Data Handling   | pandas                  |
| Styling         | Custom CSS + Streamlit themes |

---

## 🔧 Customization

### Change Theme Colors
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#4F46E5"        # Change to your brand color
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F4FF"
textColor = "#1F2937"
font = "sans serif"
```

### Add New Leave Types
Edit the `leave_type` selectbox options in `app.py` (search for `st.selectbox("Leave Type"`).

### Connect External Database
Replace the SQLite connection in `database.py`'s `get_connection()` with PostgreSQL, MySQL, or MongoDB. All other functions use the same cursor-based interface.

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

## 🤝 Support

For issues or questions, please open an issue on your GitHub repository.

Built with ❤️ using Streamlit.
