from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class TimeEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    date: date
    hours: float
    activity: Optional[str] = None
    source: str = "chat"
    raw_input: Optional[str] = None
    llm_confidence: Optional[float] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
