from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, LeaveRequest, StatusEnum
from schemas import CalendarEntry
from auth import get_current_user

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get("/week", response_model=list[CalendarEntry])
def team_calendar(
    leave_type_id: Optional[int] = Query(None, description="Filter by leave type"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    today = date.today()
    # Show this week (Mon) to next week (Sun)
    start_of_week = today - timedelta(days=today.weekday())   # This Monday
    end_of_next_week = start_of_week + timedelta(days=13)      # Next Sunday

    q = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.status == StatusEnum.approved,
            LeaveRequest.start_date <= end_of_next_week,
            LeaveRequest.end_date   >= start_of_week,
        )
    )
    if leave_type_id:
        q = q.filter(LeaveRequest.leave_type_id == leave_type_id)

    requests = q.all()

    result = []
    for lr in requests:
        result.append(CalendarEntry(
            employee_name=lr.employee.name,
            department=lr.employee.department,
            leave_type=lr.leave_type.name,
            start_date=lr.start_date,
            end_date=lr.end_date,
            working_days=lr.working_days,
        ))
    return result


@router.get("/upcoming", response_model=list[CalendarEntry])
def upcoming_leaves(
    days: int = Query(30, description="Look ahead N days"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Returns all approved leaves in the next N days."""
    today = date.today()
    until = today + timedelta(days=days)

    requests = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.status == StatusEnum.approved,
            LeaveRequest.start_date >= today,
            LeaveRequest.start_date <= until,
        )
        .order_by(LeaveRequest.start_date)
        .all()
    )

    return [
        CalendarEntry(
            employee_name=lr.employee.name,
            department=lr.employee.department,
            leave_type=lr.leave_type.name,
            start_date=lr.start_date,
            end_date=lr.end_date,
            working_days=lr.working_days,
        )
        for lr in requests
    ]