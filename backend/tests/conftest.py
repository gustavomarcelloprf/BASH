import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

# Set SECRET_KEY before importing app
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing")

from app.main import app
from app.database import get_session
from app.models.project import Project
from app.models.user import User
from app.routers.auth import hash_password


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        admin = User(
            name="Admin",
            email="admin@dash.local",
            hashed_password=hash_password("dash123"),
            role="admin",
        )
        member = User(
            name="Dev",
            email="dev@dash.local",
            hashed_password=hash_password("dash123"),
            role="member",
        )
        session.add(admin)
        session.add(member)
        session.commit()

        project = Project(name="Projeto Teste", name_raw="projeto teste", budget_hours=10.0)
        session.add(project)
        session.commit()

        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient):
    resp = client.post(
        "/api/auth/login",
        json={"email": "admin@dash.local", "password": "dash123"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="member_headers")
def member_headers_fixture(client: TestClient):
    resp = client.post(
        "/api/auth/login",
        json={"email": "dev@dash.local", "password": "dash123"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
