from datetime import date, timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from sqlmodel import Session, select

from ..database import get_session
from ..models.entry import TimeEntry
from ..models.project import Project
from ..models.user import User
from ..services.report_generator import generate_pdf
from .auth import get_admin_user

router = APIRouter(prefix="/api/reports", tags=["reports"])


class ReportRequest(BaseModel):
    period: str = "month"
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    matter_id: Optional[int] = None
    user_id: Optional[int] = None


def _date_range(req: ReportRequest) -> tuple[date, date]:
    today = date.today()
    if req.period == "custom" and req.date_from and req.date_to:
        return date.fromisoformat(req.date_from), date.fromisoformat(req.date_to)
    return today.replace(day=1), today


@router.post("/generate")
def generate_report(
    body: ReportRequest,
    current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[Session, Depends(get_session)],
) -> Response:
    start, end = _date_range(body)

    stmt = select(TimeEntry).where(
        TimeEntry.is_active == True,
        TimeEntry.date >= start,
        TimeEntry.date <= end,
    )
    if body.matter_id:
        stmt = stmt.where(TimeEntry.project_id == body.matter_id)
    if body.user_id:
        stmt = stmt.where(TimeEntry.user_id == body.user_id)

    raw_entries = session.exec(stmt).all()

    # Enrich with project/user names
    projects = {p.id: p for p in session.exec(select(Project)).all()}
    users = {u.id: u for u in session.exec(select(User)).all()}

    entries = [
        {
            "project_id": e.project_id,
            "project_name": projects[e.project_id].name if e.project_id in projects else f"Projeto {e.project_id}",
            "budget_hours": projects[e.project_id].budget_hours if e.project_id in projects else 0.0,
            "user_id": e.user_id,
            "user_name": users[e.user_id].name if e.user_id in users else f"Usuário {e.user_id}",
            "hours": e.hours,
            "date": str(e.date),
        }
        for e in raw_entries
    ]

    months_pt = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
    ]
    if body.period == "custom":
        period_label = f"{start.strftime('%d/%m/%Y')} – {end.strftime('%d/%m/%Y')}"
    else:
        period_label = f"{months_pt[start.month - 1]} {start.year}"

    pdf_bytes = generate_pdf(entries, period_label)

    filename = f"relatorio_{start.year}_{start.month:02d}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
