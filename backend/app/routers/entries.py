from datetime import date, datetime, timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, field_validator
from sqlmodel import Session, select

from ..database import get_session
from ..models.entry import TimeEntry
from ..models.project import Project
from ..models.user import User
from ..services.parser import ParseResult, parse
from .auth import get_current_user

router = APIRouter(prefix="/api/entries", tags=["entries"])


class EntryCreate(BaseModel):
    project_id: int
    date: date
    hours: float
    activity: Optional[str] = None
    source: str = "chat"
    raw_input: Optional[str] = None
    llm_confidence: Optional[float] = None

    @field_validator("hours")
    @classmethod
    def hours_must_be_valid(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("hours must be greater than 0")
        if v > 24:
            raise ValueError("hours cannot exceed 24")
        return v


class EntryUpdate(BaseModel):
    project_id: Optional[int] = None
    date: Optional[date] = None
    hours: Optional[float] = None
    activity: Optional[str] = None
    source: Optional[str] = None
    raw_input: Optional[str] = None
    llm_confidence: Optional[float] = None

    @field_validator("hours")
    @classmethod
    def hours_must_be_valid(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v <= 0:
                raise ValueError("hours must be greater than 0")
            if v > 24:
                raise ValueError("hours cannot exceed 24")
        return v


class EntryOut(BaseModel):
    id: int
    project_id: int
    user_id: int
    date: date
    hours: float
    activity: Optional[str]
    source: str
    raw_input: Optional[str]
    llm_confidence: Optional[float]
    created_at: datetime


def _period_filter(period: Optional[str]) -> Optional[date]:
    if period == "month":
        today = date.today()
        return today.replace(day=1)
    if period == "week":
        today = date.today()
        return today - timedelta(days=today.weekday())
    return None


@router.get("", response_model=list[EntryOut])
def list_entries(
    period: Annotated[Optional[str], Query()] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    query = select(TimeEntry).where(
        TimeEntry.user_id == current_user.id,
        TimeEntry.is_active == True,
    )
    since = _period_filter(period)
    if since:
        query = query.where(TimeEntry.date >= since)
    return session.exec(query).all()


@router.post("", response_model=EntryOut, status_code=status.HTTP_201_CREATED)
def create_entry(
    body: EntryCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    entry = TimeEntry(**body.model_dump(), user_id=current_user.id)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.put("/{entry_id}", response_model=EntryOut)
def update_entry(
    entry_id: int,
    body: EntryUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    entry = session.get(TimeEntry, entry_id)
    if not entry or not entry.is_active:
        raise HTTPException(status_code=404, detail="registro não encontrado")
    if entry.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="sem permissão para esta operação")

    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(entry, k, v)

    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    entry = session.get(TimeEntry, entry_id)
    if not entry or not entry.is_active:
        raise HTTPException(status_code=404, detail="registro não encontrado")
    if entry.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="sem permissão para esta operação")

    entry.is_active = False
    session.add(entry)
    session.commit()


class ParseRequest(BaseModel):
    text: str


@router.post("/parse", response_model=ParseResult)
async def parse_entry(
    body: ParseRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    projects = [
        p.name
        for p in session.exec(
            select(Project).where(Project.status == "active")
        ).all()
    ]
    return await parse(body.text, projects)
