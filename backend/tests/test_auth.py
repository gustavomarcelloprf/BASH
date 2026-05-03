from datetime import date

from sqlmodel import Session, select

from app.models.entry import TimeEntry
from app.models.project import Project
from app.models.user import User


def test_login_success(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "admin@dash.local", "password": "dash123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "admin@dash.local", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


def test_me_without_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_valid_token(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "admin@dash.local"
    assert data["role"] == "admin"


def test_admin_can_delete_any_entry(client, session: Session, auth_headers, member_headers):
    member = session.exec(select(User).where(User.email == "dev@dash.local")).first()
    project = session.exec(select(Project)).first()
    entry = TimeEntry(
        project_id=project.id,
        user_id=member.id,
        date=date.today(),
        hours=1.0,
        source="chat",
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)

    resp = client.delete(f"/api/entries/{entry.id}", headers=auth_headers)
    assert resp.status_code == 204


def test_member_cannot_delete_others_entry(client, session: Session, auth_headers, member_headers):
    admin = session.exec(select(User).where(User.email == "admin@dash.local")).first()
    project = session.exec(select(Project)).first()
    entry = TimeEntry(
        project_id=project.id,
        user_id=admin.id,
        date=date.today(),
        hours=2.0,
        source="chat",
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)

    resp = client.delete(f"/api/entries/{entry.id}", headers=member_headers)
    assert resp.status_code == 403


def test_member_cannot_access_roi(client, member_headers):
    resp = client.get("/api/dashboard/roi", headers=member_headers)
    assert resp.status_code == 403


def test_admin_can_access_roi(client, auth_headers):
    resp = client.get("/api/dashboard/roi", headers=auth_headers)
    assert resp.status_code == 200
