# TaskFlow - Agile Kanban & Issue Tracker

An Agile Task & Issue Tracker (Mini-Jira / Trello) built with **Python**, **Django**, **Tailwind CSS**, and **SortableJS**.

---

## 🌟 Key Features

1. **Interactive Drag-and-Drop Kanban Board:**
   - Drag task cards smoothly between columns (*To Do*, *In Progress*, *Review*, *Done*) and reorder them.
   - Built with SortableJS and connects asynchronously to a Django API endpoint (`/api/tasks/<id>/move/`) using `fetch()` and CSRF protection.
2. **Projects & Team Collaboration:**
   - Create projects, customize workflow columns, and invite team members.
   - Assign tasks to members with priority labels (*Urgent*, *High*, *Medium*, *Low*) and due dates.
3. **Task Details & Live Comments:**
   - Click any card to open a modal showing description, assignee, priority, and threaded discussion comments.
4. **Activity Audit Log:**
   - Real-time logging of task moves, creations, and updates in a slide-over drawer.
5. **Full Django Authentication & Admin:**
   - User registration, login, logout, and full Django Admin portal at `/admin/`.

---

## 🚀 Quick Start Guide

### 1. Activate the Virtual Environment
```powershell
cd C:\Users\hp\.gemini\antigravity\scratch\taskflow
.\.venv\Scripts\Activate.ps1
```

### 2. Run Database Migrations & Seed Sample Data
The database is already initialized and seeded with demo tasks and users. If you ever need to reset or re-seed:
```powershell
python manage.py migrate
python manage.py seed_data
```

### 3. Start the Development Server
```powershell
python manage.py runserver
```

Open your browser and navigate to: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Demo Credentials

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin / Superuser** | `admin` | `admin123` |
| **Team Member** | `sarah` | `password123` |

You can also click **"Get Started"** on the navbar to register your own new account.

---

## 📁 Project Architecture

```
taskflow/
├── config/              # Django settings & root URL configurations
├── boards/              # Core application
│   ├── models.py        # Project, Column, Task, TaskComment, ActivityLog models
│   ├── views.py         # Board views, auth, and async move APIs
│   ├── urls.py          # App routing
│   ├── forms.py         # Project, Task, and Column forms
│   ├── admin.py         # Django admin model registrations
│   └── management/      # Custom management commands (seed_data)
├── templates/           # HTML templates styled with Tailwind CSS
│   ├── base.html        # Shared navigation, flash messages, and styling
│   ├── boards/
│   │   ├── project_list.html  # Dashboard & projects overview
│   │   └── board.html         # Interactive Kanban workspace & SortableJS
│   └── registration/
│       ├── login.html
│       └── register.html
├── static/              # Static assets
├── db.sqlite3           # SQLite database
├── requirements.txt     # Python dependencies
└── manage.py            # Django CLI management script
```

