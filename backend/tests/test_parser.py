from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models.user import User
from app.routers.auth import hash_password
from app.services.parser import parse_regex


# ── Regex unit tests (parametrize) ──────────────────────────────────────────

@pytest.mark.parametrize("text,expected_hours,expected_confidence,check_date", [
    ("2h na petição do caso Silva",       2.0,  0.85, None),
    ("trabalhei 1h30 no contrato alfa",   1.5,  0.85, None),
    ("reunião de 45min com cliente",      0.75, 0.85, None),
    ("meia hora de revisão",              0.5,  0.85, None),
    ("ontem fiz 3h no processo 0042",     3.0,  0.85, "ontem"),
    ("2,5h audiência",                    2.5,  0.85, None),
    ("fiz algumas coisas hoje",           None, 0.0,  None),
    ("8h30 levantamento",                 8.5,  0.85, None),
])
def test_regex_parser(text, expected_hours, expected_confidence, check_date):
    result = parse_regex(text)
    assert result.hours == expected_hours, f"hours mismatch for '{text}': {result.hours}"
    assert result.confidence == expected_confidence, f"confidence mismatch for '{text}': {result.confidence}"
    if check_date == "ontem":
        expected = (date.today() - timedelta(days=1)).isoformat()
        assert result.date == expected, f"date mismatch for '{text}': {result.date}"


# ── Endpoint tests ───────────────────────────────────────────────────────────

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(
            name="Admin",
            email="admin@dash.local",
            hashed_password=hash_password("dash123"),
            role="admin",
        )
        session.add(user)
        session.commit()
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def override():
        yield session

    app.dependency_overrides[get_session] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient):
    resp = client.post(
        "/api/auth/login",
        json={"email": "admin@dash.local", "password": "dash123"},
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_parse_endpoint_returns_preview(client, auth_headers, session):
    from sqlmodel import select
    from app.models.entry import TimeEntry

    entries_before = session.exec(select(TimeEntry)).all()

    resp = client.post(
        "/api/entries/parse",
        json={"text": "2h na petição do caso Silva"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["hours"] == 2.0
    assert data["source"] == "regex"

    entries_after = session.exec(select(TimeEntry)).all()
    assert len(entries_before) == len(entries_after), "parse endpoint must not create entries"


def test_parse_endpoint_requires_auth(client):
    resp = client.post(
        "/api/entries/parse",
        json={"text": "2h na petição do caso Silva"},
    )
    assert resp.status_code == 401
