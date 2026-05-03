from datetime import date, timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlmodel import Session, func, select

from ..database import get_session
from ..models.entry import TimeEntry
from ..models.project import Project
from ..models.user import User
from ..services.roi import calculate_roi
from .auth import get_admin_user, get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

_PT_MONTHS = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def _period_dates(period: str, date_from: Optional[date], date_to: Optional[date]):
    today = date.today()
    if period == "week":
        start = today - timedelta(days=today.weekday())
        return start, today
    if period == "custom" and date_from and date_to:
        return date_from, date_to
    # month (default)
    return today.replace(day=1), today


class SummaryOut(BaseModel):
    total_hours: float
    active_projects: int
    entries_count: int
    roi_hours_saved: float
    roi_cost_saved: float
    period_label: str


class AlertOut(BaseModel):
    project_id: int
    project_name: str
    budget_hours: float
    consumed_hours: float
    percent: float
    status: str


class RoiOut(BaseModel):
    since: Optional[str]
    total_entries_automated: int
    total_hours_saved: float
    total_cost_saved: float
    avg_minutes_per_entry_manual: float


@router.get("/summary", response_model=SummaryOut)
def summary(
    period: Annotated[str, Query()] = "month",
    date_from: Annotated[Optional[date], Query()] = None,
    date_to: Annotated[Optional[date], Query()] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    start, end = _period_dates(period, date_from, date_to)

    base = select(TimeEntry).where(
        TimeEntry.user_id == current_user.id,
        TimeEntry.is_active == True,
        TimeEntry.date >= start,
        TimeEntry.date <= end,
    )

    entries = session.exec(base).all()
    total_hours = round(sum(e.hours for e in entries), 2)
    active_projects = len({e.project_id for e in entries})
    entries_count = len(entries)

    roi = calculate_roi(entries_count, current_user.hourly_rate or 100.0)
    today = date.today()
    label = f"{_PT_MONTHS[today.month - 1]} {today.year}"

    return SummaryOut(
        total_hours=total_hours,
        active_projects=active_projects,
        entries_count=entries_count,
        roi_hours_saved=roi["hours_saved"],
        roi_cost_saved=roi["cost_saved"],
        period_label=label,
    )


@router.get("/alerts", response_model=list[AlertOut])
def alerts(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    cutoff = date.today() - timedelta(days=30)
    projects = session.exec(
        select(Project).where(Project.budget_hours > 0, Project.status == "active")
    ).all()

    result: list[AlertOut] = []
    for p in projects:
        entries = session.exec(
            select(TimeEntry).where(
                TimeEntry.project_id == p.id,
                TimeEntry.is_active == True,
                TimeEntry.date >= cutoff,
            )
        ).all()
        consumed = round(sum(e.hours for e in entries), 2)
        percent = consumed / p.budget_hours
        if percent < 0.8:
            continue
        result.append(
            AlertOut(
                project_id=p.id,
                project_name=p.name,
                budget_hours=p.budget_hours,
                consumed_hours=consumed,
                percent=round(percent, 4),
                status="critical" if percent >= 1.0 else "warning",
            )
        )

    result.sort(key=lambda a: a.percent, reverse=True)
    return result


@router.get("/roi", response_model=RoiOut)
def roi_endpoint(
    current_user: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
):
    chat_entries = session.exec(
        select(TimeEntry).where(TimeEntry.source == "chat", TimeEntry.is_active == True)
    ).all()

    total = len(chat_entries)
    since = None
    if chat_entries:
        since = str(min(e.created_at for e in chat_entries).date())

    roi = calculate_roi(total)
    return RoiOut(
        since=since,
        total_entries_automated=total,
        total_hours_saved=roi["hours_saved"],
        total_cost_saved=roi["cost_saved"],
        avg_minutes_per_entry_manual=roi["avg_minutes_per_entry_manual"],
    )
