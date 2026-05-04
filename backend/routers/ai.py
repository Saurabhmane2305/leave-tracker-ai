import os, json
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from groq import Groq

from database import get_db
from models import User, LeaveRequest, LeaveBalance, LeaveType, StatusEnum, RoleEnum
from schemas import (
    NLParseRequest, NLParseResponse,
    ChatRequest, ChatResponse,
    PatternReportResponse, ApprovalInsightResponse,
)
from auth import get_current_user, require_manager

router = APIRouter(prefix="/ai", tags=["AI"])

def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
    return Groq(api_key=api_key)

MODEL = "llama-3.3-70b-versatile"


# ─── 1. Natural Language Leave Parsing ───────────────────────────────────────

@router.post("/parse-leave", response_model=NLParseResponse)
def parse_leave_nl(
    payload: NLParseRequest,
    _: User = Depends(get_current_user),
):
    """
    Employee types: 'I need next Monday and Tuesday off for a family function'
    Returns: structured leave data to pre-fill the form.
    """
    client = get_groq_client()
    today_str = date.today().isoformat()

    system_prompt = f"""You are a leave request parser for an internal HR tool.
Today's date is {today_str}.
The user will describe their leave in natural language.

Extract and return ONLY a JSON object with these fields:
- leave_type: one of "Sick", "Casual", "WFH", "Comp-off" (infer from context; default "Casual")
- start_date: ISO date string (YYYY-MM-DD)
- end_date: ISO date string (YYYY-MM-DD)
- reason: a clean, professional one-line reason
- confidence: float between 0 and 1 indicating how confident you are

Rules:
- "next Monday" means the upcoming Monday from today
- If only one day is mentioned, start_date == end_date
- If dates are ambiguous, use your best guess and set confidence < 0.7
- Return ONLY raw JSON, no markdown, no explanation."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": payload.text},
        ],
        temperature=0.1,
        max_tokens=300,
    )

    raw = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON from the response
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
        else:
            return NLParseResponse(raw_response=raw)

    return NLParseResponse(
        leave_type=parsed.get("leave_type"),
        start_date=parsed.get("start_date"),
        end_date=parsed.get("end_date"),
        reason=parsed.get("reason"),
        confidence=parsed.get("confidence"),
        raw_response=raw,
    )


# ─── 2. Smart Approval Insights ──────────────────────────────────────────────

@router.post("/approval-insights/{request_id}", response_model=ApprovalInsightResponse)
def approval_insights(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """
    For a pending leave request, give manager an AI summary:
    - Is the employee's balance sufficient?
    - Are there conflicts with the team?
    - Any patterns to flag?
    """
    lr = db.query(LeaveRequest).filter_by(id=request_id).first()
    if not lr:
        raise HTTPException(status_code=404, detail="Leave request not found")

    # Gather context
    year = lr.start_date.year
    balance = db.query(LeaveBalance).filter_by(
        user_id=lr.employee_id, leave_type_id=lr.leave_type_id, year=year
    ).first()
    remaining = (balance.leave_type.yearly_quota - balance.used) if balance else "Unknown"

    # Team conflicts: anyone else approved during same period?
    conflicts = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id != lr.employee_id,
        LeaveRequest.status == StatusEnum.approved,
        LeaveRequest.start_date <= lr.end_date,
        LeaveRequest.end_date   >= lr.start_date,
    ).all()
    conflict_names = [c.employee.name for c in conflicts]

    # Past leave count this year
    past_leaves = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == lr.employee_id,
        LeaveRequest.status == StatusEnum.approved,
    ).count()

    context = f"""
Leave Request Details:
- Employee: {lr.employee.name} ({lr.employee.department})
- Leave Type: {lr.leave_type.name}
- Dates: {lr.start_date} to {lr.end_date} ({lr.working_days} working days)
- Reason: {lr.reason}
- Remaining balance for this leave type: {remaining} days
- Approved leaves this year (all types): {past_leaves}
- Team members also on leave during this period: {', '.join(conflict_names) if conflict_names else 'None'}
"""

    client = get_groq_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are an HR assistant helping a manager decide on a leave request.
Provide a concise insight (3-5 sentences) covering:
1. Whether the balance is sufficient
2. Any team availability concerns
3. A brief recommendation (approve/reject/flag)
Be professional, factual, and helpful. No fluff.""",
            },
            {"role": "user", "content": context},
        ],
        temperature=0.3,
        max_tokens=400,
    )

    insights = response.choices[0].message.content.strip()
    return ApprovalInsightResponse(request_id=request_id, insights=insights)


# ─── 3. Pattern Detection ─────────────────────────────────────────────────────

@router.get("/pattern-report/{employee_id}", response_model=PatternReportResponse)
def pattern_report(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """
    Analyses an employee's leave history and flags suspicious patterns.
    E.g. repeated Mondays/Fridays, frequent sick leaves, etc.
    """
    emp = db.query(User).filter_by(id=employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    leaves = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.status == StatusEnum.approved,
    ).order_by(LeaveRequest.start_date).all()

    if not leaves:
        return PatternReportResponse(
            employee_id=employee_id,
            employee_name=emp.name,
            report="No approved leave history found to analyse.",
        )

    # Build leave summary
    leave_summary = []
    for lr in leaves:
        day_of_week = lr.start_date.strftime("%A")
        leave_summary.append(
            f"- {lr.leave_type.name} leave: {lr.start_date} ({day_of_week}) to {lr.end_date}, {lr.working_days} day(s). Reason: {lr.reason}"
        )

    context = "\n".join(leave_summary)

    client = get_groq_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are an HR analytics assistant. Analyse the employee's leave history below.
Identify patterns such as:
- Frequent leaves on Mondays or Fridays (long-weekend farming)
- High frequency of sick leaves
- Leaves clustered around specific months
- Any other unusual patterns

Provide a clear, professional report in 4-6 sentences.
If no suspicious patterns are found, say so clearly.
Do not make accusations — just observations.""",
            },
            {
                "role": "user",
                "content": f"Employee: {emp.name}\nLeave History:\n{context}",
            },
        ],
        temperature=0.3,
        max_tokens=500,
    )

    report = response.choices[0].message.content.strip()
    return PatternReportResponse(
        employee_id=employee_id,
        employee_name=emp.name,
        report=report,
    )


# ─── 4. Conversational Leave Assistant (Streaming) ────────────────────────────

@router.post("/chat")
async def chat_assistant(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Full chat interface. Knows the user's balance, history, and can guide them
    to apply for leave. Streams token-by-token.
    """
    # Build user context
    year = date.today().year
    balances = db.query(LeaveBalance).filter_by(user_id=current_user.id, year=year).all()
    balance_str = "\n".join(
        f"- {b.leave_type.name}: {b.leave_type.yearly_quota - b.used} days remaining (used {b.used}/{b.leave_type.yearly_quota})"
        for b in balances
    )

    pending_count = db.query(LeaveRequest).filter_by(
        employee_id=current_user.id, status=StatusEnum.pending
    ).count()

    system_prompt = f"""You are a friendly HR assistant for Unico Connect's internal leave tracker.
You are talking to {current_user.name} ({current_user.role.value}, {current_user.department or 'N/A'}).

Their current leave balance ({year}):
{balance_str}
Pending requests: {pending_count}

You can help them:
- Check their leave balance
- Understand leave types (Sick, Casual, WFH, Comp-off)
- Apply for leave (guide them step-by-step; at the end say "apply_leave_intent" if they want to apply)
- Check who's on leave this week
- Understand their leave history

Be concise, warm, and helpful. Today is {date.today().isoformat()}.
If they want to actually apply for leave, collect: leave type, start date, end date, reason — then reply with:
APPLY_INTENT: {{"leave_type": "...", "start_date": "...", "end_date": "...", "reason": "..."}}
so the frontend can auto-fill the form."""

    client = get_groq_client()

    messages = [{"role": "system", "content": system_prompt}]
    for msg in payload.messages:
        messages.append({"role": msg.role, "content": msg.content})

    def generate():
        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=600,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    return StreamingResponse(generate(), media_type="text/plain")