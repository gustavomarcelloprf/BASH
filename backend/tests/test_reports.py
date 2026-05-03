import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.entry import TimeEntry
from app.models.project import Project
from datetime import date


def test_report_generates_pdf(client: TestClient, auth_headers: dict, session: Session):
    # seed a project and entry
    project = session.exec(
        __import__("sqlmodel", fromlist=["select"]).select(Project).where(Project.name == "Projeto Teste")
    ).first()
    assert project is not None

    from app.models.user import User
    user = session.exec(
        __import__("sqlmodel", fromlist=["select"]).select(User).where(User.email == "admin@dash.local")
    ).first()

    entry = TimeEntry(
        project_id=project.id,
        user_id=user.id,
        date=date.today(),
        hours=2.5,
        source="chat",
    )
    session.add(entry)
    session.commit()

    resp = client.post(
        "/api/reports/generate",
        json={"period": "month"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:4] == b"%PDF"


def test_report_requires_admin(client: TestClient, member_headers: dict):
    resp = client.post(
        "/api/reports/generate",
        json={"period": "month"},
        headers=member_headers,
    )
    assert resp.status_code == 403


def test_report_custom_period(client: TestClient, auth_headers: dict, session: Session):
    resp = client.post(
        "/api/reports/generate",
        json={
            "period": "custom",
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.content[:4] == b"%PDF"
