# 🗓 LeaveTrack — AI-Powered Leave & Time-Off Tracker

> **Unico Connect AI Intern Assessment | May 2026**
> Built with FastAPI · SQLite · React · Groq (Llama 3.3)

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Features](#features)
4. [Project Structure](#project-structure)
5. [Prerequisites](#prerequisites)
6. [Backend Setup](#backend-setup)
7. [Frontend Setup](#frontend-setup)
8. [Environment Variables](#environment-variables)
9. [Seed Data & Test Credentials](#seed-data--test-credentials)
10. [API Reference](#api-reference)
11. [AI Features](#ai-features)
12. [Known Issues & Fixes](#known-issues--fixes)
13. [Git Commit History](#git-commit-history)

---

## Project Overview

LeaveTrack is a full-stack leave management system with AI capabilities. Employees apply for leave, managers approve or reject with AI-generated insights, and admins oversee the entire organization. An AI chat assistant powered by Groq's Llama 3.3 lets employees manage leaves in plain English.

---

## Tech Stack

| Layer           | Technology                                 |
| --------------- | ------------------------------------------ |
| Backend         | FastAPI, SQLAlchemy, SQLite                |
| Auth            | JWT (python-jose), bcrypt (passlib)        |
| AI              | Groq API — `llama-3.3-70b-versatile`       |
| Frontend        | React 18, Vite, plain CSS                  |
| HTTP client fix | `httpx==0.27.0` (required for groq compat) |

---

## Features

### Employee

- Dashboard with leave balance cards and usage bars
- Apply for leave (manual form or AI natural language parser)
- View and filter leave history
- Cancel pending requests
- AI chat assistant (streaming)

### Manager

- Dashboard with pending count and team on-leave stats
- Approve / reject leaves with optional comment
- AI insights per leave request (team availability, conflicts, patterns)
- Team calendar — this week and next week

### Super Admin

- Stats dashboard (total employees, requests, pending, approved)
- View all leave requests across the org
- User management — create users, change roles
- Team calendar

---

## Project Structure

```
leave-tracker/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # SQLAlchemy engine + session
│   ├── models.py                # DB models (User, LeaveRequest, etc.)
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── auth.py                  # JWT utils (create/verify token)
│   ├── seed.py                  # Seed script — run once
│   ├── requirements.txt
│   ├── .env                     # Secret keys and API keys
│   └── routers/
│       ├── auth.py              # POST /auth/login, GET /auth/me
│       ├── leaves.py            # Employee leave endpoints
│       ├── users.py             # User list, create, managers dropdown
│       ├── manager.py           # Approve/reject endpoints
│       ├── admin.py             # Admin stats and all-leaves view
│       ├── calendar.py          # Week calendar
│       └── ai.py                # All 4 AI features
│
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── main.jsx             # React entry point
        ├── App.jsx              # Role-based routing
        ├── index.css            # All styles
        ├── api/
        │   └── index.js         # All API calls
        ├── context/
        │   └── AuthContext.jsx  # JWT auth state
        ├── components/
        │   └── Layout.jsx       # Sidebar + topbar
        └── pages/
            ├── LoginPage.jsx
            ├── EmployeeDashboard.jsx
            ├── ApplyLeavePage.jsx
            ├── MyLeavesPage.jsx
            ├── ManagerDashboard.jsx
            ├── PendingApprovalsPage.jsx
            ├── CalendarPage.jsx
            ├── ChatPage.jsx
            └── AdminPages.jsx
```

---

## Prerequisites

Make sure you have these installed:

- **Python 3.10+** — `python --version`
- **Node.js 18+** — `node --version`
- **npm** — `npm --version`
- **Git**
- A **Groq API key** — get one free at [console.groq.com](https://console.groq.com)

---

## Backend Setup

### 1. Navigate to backend

```bash
cd leave-tracker/backend
```

### 2. Create and activate virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ **Critical:** After installing, fix the Groq + httpx version conflict:
>
> ```bash
> pip install httpx==0.27.0
> ```
>
> Without this, the Groq client throws `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`

### 4. Create `.env` file

```bash
# Windows
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

Then open `.env` and fill in your Groq API key (see [Environment Variables](#environment-variables) below).

### 5. Seed the database

```bash
python seed.py
```

This creates `leave_tracker.db` with 1 admin, 3 managers, 16 employees, 4 leave types, and ~30 sample leave requests.

### 6. Start the backend server

```bash
uvicorn main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`
API docs (Swagger): `http://localhost:8000/docs`

---

## Frontend Setup

### 1. Navigate to frontend

```bash
cd leave-tracker/frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Start dev server

```bash
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## Environment Variables

Create `backend/.env` with the following:

```env
SECRET_KEY=supersecretkey123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
GROQ_API_KEY=your-groq-api-key-here
DATABASE_URL=sqlite:///./leave_tracker.db
```

| Variable                      | Description                                    |
| ----------------------------- | ---------------------------------------------- |
| `SECRET_KEY`                  | JWT signing secret — change this in production |
| `ALGORITHM`                   | JWT algorithm — keep as `HS256`                |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes (480 = 8 hours)      |
| `GROQ_API_KEY`                | Your Groq API key from console.groq.com        |
| `DATABASE_URL`                | SQLite file path — no changes needed           |

---

## Seed Data & Test Credentials

After running `python seed.py`, these accounts are available:

| Role                | Email                                      | Password     |
| ------------------- | ------------------------------------------ | ------------ |
| Super Admin         | admin@unico.com                            | admin123     |
| Manager 1           | priya@unico.com                            | manager123   |
| Manager 2           | rohan@unico.com                            | manager123   |
| Manager 3           | sneha@unico.com                            | manager123   |
| Employee (sample)   | aditya@unico.com                           | Password@123 |
| All other employees | employee1@unico.com … employee16@unico.com | emp123       |

**Leave Types seeded:**

| Type     | Yearly Quota |
| -------- | ------------ |
| Sick     | 12 days      |
| Casual   | 12 days      |
| WFH      | 24 days      |
| Comp-off | 6 days       |

---

## API Reference

### Auth

| Method | Endpoint      | Description                  | Auth |
| ------ | ------------- | ---------------------------- | ---- |
| POST   | `/auth/login` | Email + password → JWT token | No   |
| GET    | `/auth/me`    | Current logged-in user info  | Yes  |

### Employee — Leaves

| Method | Endpoint          | Description                                   |
| ------ | ----------------- | --------------------------------------------- |
| POST   | `/leaves/apply`   | Submit a leave request                        |
| GET    | `/leaves/my`      | My leave history (optional `?status=pending`) |
| GET    | `/leaves/balance` | My balance per leave type                     |
| DELETE | `/leaves/{id}`    | Cancel a pending leave                        |

### Manager

| Method | Endpoint                       | Description                   |
| ------ | ------------------------------ | ----------------------------- |
| GET    | `/manager/pending`             | Pending leaves assigned to me |
| PATCH  | `/manager/leaves/{id}/approve` | Approve with optional comment |
| PATCH  | `/manager/leaves/{id}/reject`  | Reject with optional comment  |

### Calendar

| Method | Endpoint                 | Description                          |
| ------ | ------------------------ | ------------------------------------ |
| GET    | `/calendar/week`         | Who's on leave this week + next week |
| GET    | `/calendar/?start=&end=` | Custom date range                    |

### Admin

| Method | Endpoint                 | Description        |
| ------ | ------------------------ | ------------------ |
| GET    | `/admin/leaves`          | All leave requests |
| GET    | `/admin/stats`           | Org-wide stats     |
| PUT    | `/admin/users/{id}/role` | Change user role   |

### Users

| Method | Endpoint          | Description                  |
| ------ | ----------------- | ---------------------------- |
| GET    | `/users/`         | All users (admin only)       |
| GET    | `/users/managers` | Managers list for dropdown   |
| POST   | `/users/`         | Create new user (admin only) |

### AI

| Method | Endpoint                          | Description                        |
| ------ | --------------------------------- | ---------------------------------- |
| POST   | `/ai/parse-leave`                 | Natural language → leave fields    |
| GET    | `/ai/manager-insights/{leave_id}` | AI approval insight for a request  |
| GET    | `/ai/patterns/{employee_id}`      | Suspicious leave pattern detection |
| POST   | `/ai/chat`                        | Streaming chat assistant           |

---

## AI Features

All AI features use **Groq API** with model `llama-3.3-70b-versatile`.

### 1. NL Leave Parser — `POST /ai/parse-leave`

Send plain English, get structured leave fields back.

**Request:**

```json
{ "text": "I need Monday and Tuesday off for a family function" }
```

**Response:**

```json
{
  "start_date": "2026-05-11",
  "end_date": "2026-05-12",
  "reason": "family function",
  "leave_type_id": 2
}
```

### 2. Manager Insights — `GET /ai/manager-insights/{leave_id}`

Returns a natural language summary for the manager: team availability during the requested dates, the employee's remaining balance, and any scheduling conflicts.

### 3. Pattern Detection — `GET /ai/patterns/{employee_id}`

Analyzes leave history for suspicious patterns — repeated Mondays/Fridays, pre-holiday leaves, excessive frequency — and returns a risk summary.

### 4. AI Chat Assistant — `POST /ai/chat` (streaming)

A conversational assistant that can answer balance queries, summarize history, and guide the employee through applying for leave. Response streams token by token.

---

## Known Issues & Fixes

### Groq `proxies` TypeError

**Error:** `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`

**Cause:** Groq SDK 0.4.2 is incompatible with newer versions of `httpx`.

**Fix:**

```bash
pip install httpx==0.27.0
```

---

### Leave Type dropdown empty on Apply page

**Cause:** Backend returns leave type IDs as integers, but HTML `<select>` compares `value` as strings — causing a mismatch where the selected value never matched.

**Fix (already applied in frontend):** All `leave_type_id` and `manager_id` values are coerced with `String()` on render and `parseInt()` on submit.

---

### Filter sending `?status=all` to backend

**Cause:** The "All" filter tab was sending `?status=all` which the backend doesn't recognize as a valid enum value.

**Fix (already applied):** When filter is `'all'`, no query param is sent — the full list is fetched.

---

## Git Commit History

```
1. init: project structure and requirements
2. feat: database models and SQLAlchemy setup
3. feat: JWT auth, seed data, and user endpoints
4. feat: leave application and balance APIs
5. feat: manager approve/reject endpoints
6. feat: team calendar and admin endpoints
7. feat: AI service - all 4 features (Groq)
8. feat: frontend - auth and employee dashboard
9. feat: frontend - manager view and calendar
10. feat: frontend - AI chat assistant UI
11. fix: groq httpx version conflict, frontend form bugs
```

---

## Running Both Servers

Open two terminal windows:

**Terminal 1 — Backend:**

```bash
cd leave-tracker/backend
venv\Scripts\activate        # Windows
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd leave-tracker/frontend
npm run dev
```

Then open `http://localhost:5173` in your browser.

---

_Stack: FastAPI + SQLite + React + Vite + Groq (llama-3.3-70b-versatile)_
_Assessment: Unico Connect AI Intern | May 2026_


