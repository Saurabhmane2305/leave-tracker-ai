from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, LeaveRequest, LeaveBalance, LeaveType, AuditLog, StatusEnum, RoleEnum
from schemas import (
    LeaveApplyRequest, LeaveApplyResponse, LeaveRequestOut,
    LeaveActionRequest, LeaveBalanceOut, LeaveTypeOut
)
from auth import get_current_user, require_manager

router = APIRouter(prefix="/leaves", tags=["Leaves"])


# ─── Helpers ─────────────────────────────────────────────────────────────────

def calc_working_days(start: date, end: date) -> int:
    count, current = 0, start
    while current <= end:
        if current.weekday() < 5:
            count += 1
        current += timedelta(days=1)
    return count


# ─── Employee: Apply for Leave ────────────────────────────────────────────────

@router.post("/apply", response_model=LeaveApplyResponse, status_code=201)
def apply_leave(
    payload: LeaveApplyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate dates
    if payload.start_date > payload.end_date:
        raise HTTPException(status_code=422, detail="start_date must be before end_date")
    if payload.start_date < date.today():
        raise HTTPException(status_code=422, detail="Cannot apply for past dates")

    # Validate leave type
    lt = db.query(LeaveType).filter_by(id=payload.leave_type_id).first()
    if not lt:
        raise HTTPException(status_code=404, detail="Leave type not found")

    # Validate manager
    mgr = db.query(User).filter(User.id == payload.manager_id, User.role.in_(["manager", "super_admin"])).first()
    if not mgr:
        raise HTTPException(status_code=404, detail="Manager not found")

    # Check balance
    year = date.today().year
    balance = db.query(LeaveBalance).filter_by(
        user_id=current_user.id, leave_type_id=lt.id, year=year
    ).first()
    wdays = calc_working_days(payload.start_date, payload.end_date)
    remaining = (balance.leave_type.yearly_quota - balance.used) if balance else lt.yearly_quota

    if wdays > remaining:
        raise HTTPException(
            status_code=422,
            detail=f"Insufficient balance. Requested {wdays} days, only {remaining} remaining."
        )

    lr = LeaveRequest(
        employee_id=current_user.id,
        manager_id=payload.manager_id,
        leave_type_id=lt.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        working_days=wdays,
        reason=payload.reason,
        status=StatusEnum.pending,
    )
    db.add(lr)
    db.commit()
    db.refresh(lr)

    return LeaveApplyResponse(
        id=lr.id,
        working_days=wdays,
        status=lr.status,
        message="Leave request submitted successfully",
    )


# ─── Employee: My Leave History ───────────────────────────────────────────────

@router.get("/my", response_model=list[LeaveRequestOut])
def my_leaves(
    status: Optional[StatusEnum] = Query(None),
    from_date: Optional[date]    = Query(None),
    to_date:   Optional[date]    = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(LeaveRequest).filter(LeaveRequest.employee_id == current_user.id)
    if status:
        q = q.filter(LeaveRequest.status == status)
    if from_date:
        q = q.filter(LeaveRequest.start_date >= from_date)
    if to_date:
        q = q.filter(LeaveRequest.end_date <= to_date)
    return q.order_by(LeaveRequest.created_at.desc()).all()


# ─── Employee: My Balance ─────────────────────────────────────────────────────

@router.get("/balance", response_model=list[LeaveBalanceOut])
def my_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    year = date.today().year
    balances = db.query(LeaveBalance).filter_by(user_id=current_user.id, year=year).all()
    result = []
    for b in balances:
        result.append(LeaveBalanceOut(
            leave_type=LeaveTypeOut(id=b.leave_type.id, name=b.leave_type.name, yearly_quota=b.leave_type.yearly_quota),
            used=b.used,
            year=b.year,
            remaining=b.leave_type.yearly_quota - b.used,
        ))
    return result


# ─── Manager: Pending Requests ────────────────────────────────────────────────

@router.get("/pending", response_model=list[LeaveRequestOut])
def pending_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    if current_user.role == RoleEnum.super_admin:
        # Admin sees all pending
        return db.query(LeaveRequest).filter_by(status=StatusEnum.pending).order_by(LeaveRequest.created_at).all()
    return (
        db.query(LeaveRequest)
        .filter_by(manager_id=current_user.id, status=StatusEnum.pending)
        .order_by(LeaveRequest.created_at)
        .all()
    )


# ─── Manager: Approve ─────────────────────────────────────────────────────────

@router.patch("/{request_id}/approve", response_model=LeaveRequestOut)
def approve_leave(
    request_id: int,
    payload: LeaveActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    lr = db.query(LeaveRequest).filter_by(id=request_id).first()
    if not lr:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if lr.manager_id != current_user.id and current_user.role != RoleEnum.super_admin:
        raise HTTPException(status_code=403, detail="Not your request to manage")
    if lr.status != StatusEnum.pending:
        raise HTTPException(status_code=422, detail=f"Request is already {lr.status.value}")

    lr.status          = StatusEnum.approved
    lr.manager_comment = payload.comment
    lr.acted_at        = datetime.utcnow()

    # Update balance
    year = lr.start_date.year
    balance = db.query(LeaveBalance).filter_by(
        user_id=lr.employee_id, leave_type_id=lr.leave_type_id, year=year
    ).first()
    if balance:
        balance.used += lr.working_days

    db.add(AuditLog(
        action=f"Approved leave request #{request_id}",
        performed_by_id=current_user.id,
        target_request_id=request_id,
    ))
    db.commit()
    db.refresh(lr)
    return lr


# ─── Manager: Reject ──────────────────────────────────────────────────────────

@router.patch("/{request_id}/reject", response_model=LeaveRequestOut)
def reject_leave(
    request_id: int,
    payload: LeaveActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    lr = db.query(LeaveRequest).filter_by(id=request_id).first()
    if not lr:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if lr.manager_id != current_user.id and current_user.role != RoleEnum.super_admin:
        raise HTTPException(status_code=403, detail="Not your request to manage")
    if lr.status != StatusEnum.pending:
        raise HTTPException(status_code=422, detail=f"Request is already {lr.status.value}")

    lr.status          = StatusEnum.rejected
    lr.manager_comment = payload.comment
    lr.acted_at        = datetime.utcnow()

    db.add(AuditLog(
        action=f"Rejected leave request #{request_id}",
        performed_by_id=current_user.id,
        target_request_id=request_id,
    ))
    db.commit()
    db.refresh(lr)
    return lr


# ─── Admin: All Requests ──────────────────────────────────────────────────────

@router.get("/all", response_model=list[LeaveRequestOut])
def all_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    if current_user.role != RoleEnum.super_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return db.query(LeaveRequest).order_by(LeaveRequest.created_at.desc()).all()