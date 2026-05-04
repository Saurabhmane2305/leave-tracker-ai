from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, LeaveBalance, LeaveType, RoleEnum
from schemas import UserOut, CreateUserRequest
from auth import require_admin, get_current_user, hash_password
from datetime import date

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return db.query(User).all()


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    payload: CreateUserRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    exists = db.query(User).filter_by(email=payload.email).first()
    if exists:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        department=payload.department,
        manager_id=payload.manager_id,
    )
    db.add(user)
    db.flush()

    # Create leave balances for this user
    year = date.today().year
    for lt in db.query(LeaveType).all():
        db.add(LeaveBalance(user_id=user.id, leave_type_id=lt.id, used=0, year=year))

    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_admin),
):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current.id:
        raise HTTPException(status_code=422, detail="Cannot deactivate yourself")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.get("/managers", response_model=list[UserOut])
def list_managers(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),   # any logged-in user can fetch managers for the dropdown
):
    return db.query(User).filter(User.role.in_(["manager", "super_admin"]), User.is_active == True).all()