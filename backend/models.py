from datetime import datetime, date
from sqlalchemy import (
    Integer, String, Text, Date, DateTime, Enum, ForeignKey, Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from database import Base


# ─── Enums ───────────────────────────────────────────────────────────────────

class RoleEnum(str, enum.Enum):
    employee    = "employee"
    manager     = "manager"
    super_admin = "super_admin"


class StatusEnum(str, enum.Enum):
    pending  = "pending"
    approved = "approved"
    rejected = "rejected"


# ─── Models ──────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id:            Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    name:          Mapped[str]      = mapped_column(String(100), nullable=False)
    email:         Mapped[str]      = mapped_column(String(150), unique=True, index=True, nullable=False)
    password_hash: Mapped[str]      = mapped_column(String(255), nullable=False)
    role:          Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), default=RoleEnum.employee, nullable=False)
    department:    Mapped[str]      = mapped_column(String(100), nullable=True)
    manager_id:    Mapped[int|None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    is_active:     Mapped[bool]     = mapped_column(Boolean, default=True)
    created_at:    Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    manager:          Mapped["User"]          = relationship("User", remote_side="User.id", foreign_keys=[manager_id])
    leave_requests:   Mapped[list["LeaveRequest"]] = relationship("LeaveRequest", back_populates="employee", foreign_keys="LeaveRequest.employee_id")
    managed_requests: Mapped[list["LeaveRequest"]] = relationship("LeaveRequest", back_populates="manager",  foreign_keys="LeaveRequest.manager_id")
    balances:         Mapped[list["LeaveBalance"]]  = relationship("LeaveBalance", back_populates="user")
    audit_logs:       Mapped[list["AuditLog"]]       = relationship("AuditLog", back_populates="performed_by_user")


class LeaveType(Base):
    __tablename__ = "leave_types"

    id:           Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name:         Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # Sick, Casual, WFH, Comp-off
    yearly_quota: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    balances:       Mapped[list["LeaveBalance"]]  = relationship("LeaveBalance",  back_populates="leave_type")
    leave_requests: Mapped[list["LeaveRequest"]] = relationship("LeaveRequest", back_populates="leave_type")


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id:            Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id:       Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    leave_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("leave_types.id"), nullable=False)
    used:          Mapped[int] = mapped_column(Integer, default=0)
    year:          Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    user:       Mapped["User"]      = relationship("User",      back_populates="balances")
    leave_type: Mapped["LeaveType"] = relationship("LeaveType", back_populates="balances")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id:              Mapped[int]         = mapped_column(Integer, primary_key=True, index=True)
    employee_id:     Mapped[int]         = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    manager_id:      Mapped[int]         = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    leave_type_id:   Mapped[int]         = mapped_column(Integer, ForeignKey("leave_types.id"), nullable=False)
    start_date:      Mapped[date]        = mapped_column(Date, nullable=False)
    end_date:        Mapped[date]        = mapped_column(Date, nullable=False)
    working_days:    Mapped[int]         = mapped_column(Integer, nullable=False)
    reason:          Mapped[str]         = mapped_column(Text, nullable=False)
    status:          Mapped[StatusEnum]  = mapped_column(Enum(StatusEnum), default=StatusEnum.pending)
    manager_comment: Mapped[str|None]    = mapped_column(Text, nullable=True)
    acted_at:        Mapped[datetime|None] = mapped_column(DateTime, nullable=True)
    created_at:      Mapped[datetime]    = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    employee:   Mapped["User"]      = relationship("User",      back_populates="leave_requests",   foreign_keys=[employee_id])
    manager:    Mapped["User"]      = relationship("User",      back_populates="managed_requests",  foreign_keys=[manager_id])
    leave_type: Mapped["LeaveType"] = relationship("LeaveType", back_populates="leave_requests")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="target_request")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id:                Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    action:            Mapped[str]      = mapped_column(String(200), nullable=False)
    performed_by_id:   Mapped[int]      = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    target_request_id: Mapped[int|None] = mapped_column(Integer, ForeignKey("leave_requests.id"), nullable=True)
    timestamp:         Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    performed_by_user: Mapped["User"]         = relationship("User",         back_populates="audit_logs")
    target_request:    Mapped["LeaveRequest"] = relationship("LeaveRequest", back_populates="audit_logs")