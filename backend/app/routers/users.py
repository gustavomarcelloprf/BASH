from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, func, select

from ..database import get_session
from ..models.entry import TimeEntry
from ..models.user import User
from .auth import get_admin_user, get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    hours_this_month: float


class RolePatch(BaseModel):
    role: str


class StatusPatch(BaseModel):
    is_active: bool


@router.get("", response_model=list[UserOut])
def list_users(
    current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[Session, Depends(get_session)],
):
    users = session.exec(select(User)).all()
    today = date.today()
    month_start = today.replace(day=1)

    result = []
    for u in users:
        entries = session.exec(
            select(TimeEntry).where(
                TimeEntry.user_id == u.id,
                TimeEntry.is_active == True,
                TimeEntry.date >= month_start,
            )
        ).all()
        hours = round(sum(e.hours for e in entries), 2)
        result.append(
            UserOut(
                id=u.id,
                name=u.name,
                email=u.email,
                role=u.role,
                is_active=u.is_active,
                hours_this_month=hours,
            )
        )
    return result


@router.patch("/{user_id}/role", response_model=UserOut)
def update_role(
    user_id: int,
    body: RolePatch,
    current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[Session, Depends(get_session)],
):
    if body.role not in ("admin", "member"):
        raise HTTPException(status_code=422, detail="role deve ser 'admin' ou 'member'")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="registro não encontrado")
    if user.id == current_user.id:
        raise HTTPException(status_code=403, detail="sem permissão para esta operação")

    user.role = body.role
    session.add(user)
    session.commit()
    session.refresh(user)

    today = date.today()
    entries = session.exec(
        select(TimeEntry).where(
            TimeEntry.user_id == user.id,
            TimeEntry.is_active == True,
            TimeEntry.date >= today.replace(day=1),
        )
    ).all()
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        hours_this_month=round(sum(e.hours for e in entries), 2),
    )


@router.patch("/{user_id}/status", response_model=UserOut)
def update_status(
    user_id: int,
    body: StatusPatch,
    current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[Session, Depends(get_session)],
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="registro não encontrado")
    if user.id == current_user.id:
        raise HTTPException(status_code=403, detail="sem permissão para esta operação")

    user.is_active = body.is_active
    session.add(user)
    session.commit()
    session.refresh(user)

    today = date.today()
    entries = session.exec(
        select(TimeEntry).where(
            TimeEntry.user_id == user.id,
            TimeEntry.is_active == True,
            TimeEntry.date >= today.replace(day=1),
        )
    ).all()
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        hours_this_month=round(sum(e.hours for e in entries), 2),
    )
