from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models.entry import TimeEntry
from app.models.project import Project
from app.models.user import User
from app.routers.auth import hash_password


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(name="Admin", email="admin@dash.local", hashed_password=hash_password("dash123"), role="admin", hourly_rate=100.0)
        session.add(user)
        session.commit()
        session.refresh(user)

        p1 = Project(name="P1", name_raw="p1", budget_hours=10.0)
        p2 = Project(name="P2", name_raw="p2", budget_hours=10.0)
        p3 = Project(name="P3", name_raw="p3", budget_hours=10.0)
        session.add_all([p1, p2, p3])
        session.commit()
        session.refresh(p1); session.refresh(p2); session.refresh(p3)

        today = date.today()
        entries = [
            TimeEntry(project_id=p1.id, user_id=user.id, date=today, hours=3.0, source="chat"),
            TimeEntry(project_id=p1.id, user_id=user.id, date=today, hours=5.0, source="chat"),  # 8h/10 = 80%
            TimeEntry(project_id=p2.id, user_id=user.id, date=today, hours=9.5, source="chat"),  # 95% warning
            TimeEntry(project_id=p3.id, user_id=user.id, date=today, hours=10.5, source="chat"), # 105% critical
            TimeEntry(project_id=p1.id, user_id=user.id, date=today - timedelta(days=60), hours=2.0, source="chat"),  # outside 30d
        ]
        session.add_all(entries)
        session.commit()
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    app.dependency_overrides[get_session] = lambda: (yield session)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(name="token")
def token_fixture(client):
    r = client.post("/api/auth/login", json={"email": "admin@dash.local", "password": "dash123"})
    return r.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_summary_returns_correct_totals(client, token):
    r = client.get("/api/dashboard/summary?period=month", headers=auth(token))
    assert r.status_code == 200
    d = r.json()
    assert d["total_hours"] == 28.0   # 3+5+9.5+10.5 (all in current month; 60d-ago entry may be out)
    assert d["active_projects"] == 3
    assert d["entries_count"] == 4
    assert d["roi_hours_saved"] > 0


def test_alerts_only_above_80_percent(client, token):
    r = client.get("/api/dashboard/alerts", headers=auth(token))
    assert r.status_code == 200
    alerts = r.json()
    project_names = [a["project_name"] for a in alerts]
    assert "P2" in project_names  # 95%
    assert "P3" in project_names  # 105%


def test_alerts_ordered_by_percent_desc(client, token):
    r = client.get("/api/dashboard/alerts", headers=auth(token))
    percents = [a["percent"] for a in r.json()]
    assert percents == sorted(percents, reverse=True)


def test_roi_calculates_correctly(client, token):
    r = client.get("/api/dashboard/roi", headers=auth(token))
    assert r.status_code == 200
    d = r.json()
    assert d["total_entries_automated"] >= 0
    assert d["avg_minutes_per_entry_manual"] == 4.0
    assert d["total_hours_saved"] == round(d["total_entries_automated"] * 4.0 / 60, 2)
