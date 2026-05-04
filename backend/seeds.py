"""
Run once: python seed.py
Creates all tables and populates with realistic data.
"""
from datetime import date, timedelta, datetime
import random
from database import engine, SessionLocal
from models import Base, User, LeaveType, LeaveBalance, LeaveRequest, AuditLog, RoleEnum, StatusEnum
from auth import hash_password

random.seed(42)

DEPARTMENTS = ["Engineering", "Design", "Product", "Marketing", "Operations"]

EMPLOYEES_DATA = [
    # Super Admin
    {"name": "Aryan Shah",      "email": "admin@unico.com",      "role": RoleEnum.super_admin, "dept": "Engineering"},
    # Managers
    {"name": "Priya Menon",     "email": "priya@unico.com",      "role": RoleEnum.manager,     "dept": "Engineering"},
    {"name": "Rohan Desai",     "email": "rohan@unico.com",      "role": RoleEnum.manager,     "dept": "Design"},
    {"name": "Sneha Kulkarni",  "email": "sneha@unico.com",      "role": RoleEnum.manager,     "dept": "Product"},
    # Employees
    {"name": "Aditya Nair",     "email": "aditya@unico.com",     "role": RoleEnum.employee,    "dept": "Engineering"},
    {"name": "Meera Iyer",      "email": "meera@unico.com",      "role": RoleEnum.employee,    "dept": "Engineering"},
    {"name": "Karan Sharma",    "email": "karan@unico.com",      "role": RoleEnum.employee,    "dept": "Engineering"},
    {"name": "Tanvi Joshi",     "email": "tanvi@unico.com",      "role": RoleEnum.employee,    "dept": "Engineering"},
    {"name": "Rahul Verma",     "email": "rahul@unico.com",      "role": RoleEnum.employee,    "dept": "Design"},
    {"name": "Anjali Patil",    "email": "anjali@unico.com",     "role": RoleEnum.employee,    "dept": "Design"},
    {"name": "Vikram Singh",    "email": "vikram@unico.com",     "role": RoleEnum.employee,    "dept": "Design"},
    {"name": "Pooja Bhat",      "email": "pooja@unico.com",      "role": RoleEnum.employee,    "dept": "Design"},
    {"name": "Nikhil Rao",      "email": "nikhil@unico.com",     "role": RoleEnum.employee,    "dept": "Product"},
    {"name": "Divya Pillai",    "email": "divya@unico.com",      "role": RoleEnum.employee,    "dept": "Product"},
    {"name": "Saurabh More",    "email": "saurabh@unico.com",    "role": RoleEnum.employee,    "dept": "Product"},
    {"name": "Ishaan Mehta",    "email": "ishaan@unico.com",     "role": RoleEnum.employee,    "dept": "Marketing"},
    {"name": "Riya Kapoor",     "email": "riya@unico.com",       "role": RoleEnum.employee,    "dept": "Marketing"},
    {"name": "Ankit Gupta",     "email": "ankit@unico.com",      "role": RoleEnum.employee,    "dept": "Operations"},
    {"name": "Shruti Deshpande","email": "shruti@unico.com",     "role": RoleEnum.employee,    "dept": "Operations"},
    {"name": "Yash Pawar",      "email": "yash@unico.com",       "role": RoleEnum.employee,    "dept": "Operations"},
]

LEAVE_TYPES = [
    {"name": "Sick",     "yearly_quota": 12},
    {"name": "Casual",   "yearly_quota": 12},
    {"name": "WFH",      "yearly_quota": 24},
    {"name": "Comp-off", "yearly_quota": 6},
]

REASONS = [
    "Feeling unwell, need to rest",
    "Family function over the weekend",
    "Personal work at home",
    "Compensating for weekend overtime",
    "Medical appointment",
    "Child's school event",
    "House repair work",
    "Travel plans",
    "Mental health day",
    "Wedding in family",
]


def working_days_count(start: date, end: date) -> int:
    count = 0
    current = start
    while current <= end:
        if current.weekday() < 5:  # Mon–Fri
            count += 1
        current += timedelta(days=1)
    return count


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ── Leave Types ──────────────────────────────────────────────────────
        lt_map = {}
        for lt_data in LEAVE_TYPES:
            lt = db.query(LeaveType).filter_by(name=lt_data["name"]).first()
            if not lt:
                lt = LeaveType(**lt_data)
                db.add(lt)
                db.flush()
            lt_map[lt.name] = lt
        db.commit()

        # ── Users ────────────────────────────────────────────────────────────
        user_map = {}
        managers = []

        for u_data in EMPLOYEES_DATA:
            u = db.query(User).filter_by(email=u_data["email"]).first()
            if not u:
                u = User(
                    name=u_data["name"],
                    email=u_data["email"],
                    password_hash=hash_password("Password@123"),
                    role=u_data["role"],
                    department=u_data["dept"],
                )
                db.add(u)
                db.flush()
            user_map[u_data["email"]] = u
            if u_data["role"] == RoleEnum.manager:
                managers.append(u)

        db.commit()

        # Assign managers to employees
        employees = [u for u in user_map.values() if u.role == RoleEnum.employee]
        dept_manager = {
            "Engineering": user_map["priya@unico.com"],
            "Design":      user_map["rohan@unico.com"],
            "Product":     user_map["sneha@unico.com"],
            "Marketing":   user_map["priya@unico.com"],   # assigned to priya
            "Operations":  user_map["rohan@unico.com"],   # assigned to rohan
        }
        for emp in employees:
            emp.manager_id = dept_manager.get(emp.department, managers[0]).id
        db.commit()

        # ── Leave Balances ───────────────────────────────────────────────────
        all_users = list(user_map.values())
        year = 2026
        for u in all_users:
            for lt in lt_map.values():
                exists = db.query(LeaveBalance).filter_by(user_id=u.id, leave_type_id=lt.id, year=year).first()
                if not exists:
                    used = random.randint(0, lt.yearly_quota // 2)
                    db.add(LeaveBalance(user_id=u.id, leave_type_id=lt.id, used=used, year=year))
        db.commit()

        # ── Leave Requests ───────────────────────────────────────────────────
        today = date.today()
        statuses = [StatusEnum.pending, StatusEnum.approved, StatusEnum.rejected]
        status_weights = [0.3, 0.5, 0.2]

        leave_requests_data = []

        # Past requests (approved/rejected mostly)
        for i in range(20):
            emp = random.choice(employees)
            days_ago = random.randint(10, 90)
            start = today - timedelta(days=days_ago)
            duration = random.randint(1, 4)
            end = start + timedelta(days=duration)
            lt = random.choice(list(lt_map.values()))
            mgr = db.query(User).filter_by(id=emp.manager_id).first()
            status = random.choices(
                [StatusEnum.approved, StatusEnum.rejected],
                weights=[0.75, 0.25]
            )[0]
            leave_requests_data.append({
                "emp": emp, "mgr": mgr, "lt": lt,
                "start": start, "end": end,
                "status": status,
                "past": True,
            })

        # Upcoming / current requests (pending mostly)
        for i in range(8):
            emp = random.choice(employees)
            days_ahead = random.randint(0, 14)
            start = today + timedelta(days=days_ahead)
            duration = random.randint(1, 3)
            end = start + timedelta(days=duration)
            lt = random.choice(list(lt_map.values()))
            mgr = db.query(User).filter_by(id=emp.manager_id).first()
            status = random.choices(statuses, weights=status_weights)[0]
            leave_requests_data.append({
                "emp": emp, "mgr": mgr, "lt": lt,
                "start": start, "end": end,
                "status": status,
                "past": False,
            })

        for i, req_data in enumerate(leave_requests_data):
            emp  = req_data["emp"]
            mgr  = req_data["mgr"]
            lt   = req_data["lt"]
            start = req_data["start"]
            end   = req_data["end"]
            status = req_data["status"]
            wdays = working_days_count(start, end)

            lr = LeaveRequest(
                employee_id=emp.id,
                manager_id=mgr.id,
                leave_type_id=lt.id,
                start_date=start,
                end_date=end,
                working_days=max(wdays, 1),
                reason=random.choice(REASONS),
                status=status,
                manager_comment=(
                    random.choice(["Approved, enjoy your time!", "Take care.", "Approved."])
                    if status == StatusEnum.approved
                    else ("Please plan better next time." if status == StatusEnum.rejected else None)
                ),
                acted_at=(datetime.utcnow() if status != StatusEnum.pending else None),
            )
            db.add(lr)
            db.flush()

            # Audit log for non-pending
            if status != StatusEnum.pending:
                db.add(AuditLog(
                    action=f"Leave request {status.value} by manager",
                    performed_by_id=mgr.id,
                    target_request_id=lr.id,
                ))

        db.commit()
        print("✅ Seed complete!")
        print("─────────────────────────────────────")
        print("👤 Super Admin : admin@unico.com     / Password@123")
        print("👔 Manager 1   : priya@unico.com     / Password@123")
        print("👔 Manager 2   : rohan@unico.com     / Password@123")
        print("👔 Manager 3   : sneha@unico.com     / Password@123")
        print("👨 Employee    : aditya@unico.com    / Password@123")
        print("               (all employees use Password@123)")

    finally:
        db.close()


if __name__ == "__main__":
    seed()