# Leave Tracker AI - Architecture

## 1. Tech Stack

- Backend: FastAPI (Python)
- Frontend: React (Vite)
- Database: SQLite (lightweight, fast setup)
- AI: OpenAI / Gemini API

Reason:
Chosen for fast development, simplicity, and AI integration support.

---

## 2. Roles

### Employee
- Apply for leave
- View leave balance
- View leave history

### Manager
- Approve/reject leave requests
- View team leaves

### Super Admin
- View all users
- View system-level data (optional)

---

## 3. Database Schema

### Users
- id
- name
- email
- password
- role (employee / manager / admin)

### LeaveTypes
- id
- name (Sick, Casual, WFH, Comp-off)
- yearly_quota

### LeaveRequests
- id
- user_id
- leave_type_id
- start_date
- end_date
- days
- reason
- status (pending/approved/rejected)
- manager_id
- comment
- created_at

### LoginLogs
- id
- user_id
- login_time

---

## 4. API Endpoints

### Auth
- POST /auth/login

### Leave
- POST /leave/apply
- GET /leave/my
- GET /leave/balance

### Manager
- GET /leave/pending
- POST /leave/{id}/action

### Team
- GET /team/calendar

### AI
- POST /ai/parse-leave

---

## 5. AI Feature

Natural Language Leave Parser

User can type:
"I need next Monday off"

System extracts:
- leave type
- start date
- end date
- reason

This reduces manual form filling.

---

## 6. Folder Structure

### Backend
- main.py
- models.py
- schemas.py
- routes/

### Frontend
- src/
  - components/
  - pages/

---

## 7. Improvements (if more time)

- Notifications
- Charts
- Better UI
- Holiday calendar
