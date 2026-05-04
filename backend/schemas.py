from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, EmailStr
from models import RoleEnum, StatusEnum


# ─── Auth ────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"

class UserOut(BaseModel):
    id:         int
    name:       str
    email:      str
    role:       RoleEnum
    department: Optional[str]
    manager_id: Optional[int]
    is_active:  bool

    model_config = {"from_attributes": True}


# ─── Leave Types ─────────────────────────────────────────────────────────────

class LeaveTypeOut(BaseModel):
    id:           int
    name:         str
    yearly_quota: int

    model_config = {"from_attributes": True}


# ─── Leave Balance ───────────────────────────────────────────────────────────

class LeaveBalanceOut(BaseModel):
    leave_type:   LeaveTypeOut
    used:         int
    year:         int
    remaining:    int   # computed field

    model_config = {"from_attributes": True}


# ─── Leave Requests ──────────────────────────────────────────────────────────

class LeaveApplyRequest(BaseModel):
    leave_type_id: int
    start_date:    date
    end_date:      date
    reason:        str
    manager_id:    int

class LeaveApplyResponse(BaseModel):
    id:           int
    working_days: int
    status:       StatusEnum
    message:      str

    model_config = {"from_attributes": True}

class LeaveRequestOut(BaseModel):
    id:              int
    employee:        UserOut
    manager:         UserOut
    leave_type:      LeaveTypeOut
    start_date:      date
    end_date:        date
    working_days:    int
    reason:          str
    status:          StatusEnum
    manager_comment: Optional[str]
    acted_at:        Optional[datetime]
    created_at:      datetime

    model_config = {"from_attributes": True}

class LeaveActionRequest(BaseModel):
    comment: Optional[str] = None


# ─── Calendar ────────────────────────────────────────────────────────────────

class CalendarEntry(BaseModel):
    employee_name: str
    department:    Optional[str]
    leave_type:    str
    start_date:    date
    end_date:      date
    working_days:  int

    model_config = {"from_attributes": True}


# ─── Admin ───────────────────────────────────────────────────────────────────

class CreateUserRequest(BaseModel):
    name:       str
    email:      EmailStr
    password:   str
    role:       RoleEnum = RoleEnum.employee
    department: Optional[str] = None
    manager_id: Optional[int] = None


# ─── AI ──────────────────────────────────────────────────────────────────────

class NLParseRequest(BaseModel):
    text: str   # "I need next Monday and Tuesday off for a family function"

class NLParseResponse(BaseModel):
    leave_type:    Optional[str]   = None
    start_date:    Optional[str]   = None   # ISO string
    end_date:      Optional[str]   = None
    reason:        Optional[str]   = None
    confidence:    Optional[float] = None
    raw_response:  str

class ChatMessage(BaseModel):
    role:    str   # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]

class ChatResponse(BaseModel):
    reply: str

class PatternReportResponse(BaseModel):
    employee_id:   int
    employee_name: str
    report:        str   # AI-generated analysis

class ApprovalInsightResponse(BaseModel):
    request_id: int
    insights:   str   # AI-generated summary