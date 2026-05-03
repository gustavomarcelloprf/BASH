import io
from datetime import date, timedelta

import openpyxl
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.models.project import Project
from app.models.user import User
from app.routers.auth import hash_password
from app.services.importer import import_xlsx
from app.services.normalizer import normalize_project_name


# ── Normalizer unit tests ────────────────────────────────────────────────────

def test_normalize_exact_match():
    existing = ["Caso Silva", "Ferreira Previdenciário"]
    result = normalize_project_name("Caso Silva", existing)
    assert result == "Caso Silva"


def test_normalize_fuzzy_match():
    existing = ["Caso Silva"]
    result = normalize_project_name("caso silva", existing)
    assert result == "Caso Silva"


def test_normalize_no_match():
    existing = ["Caso Silva", "Ferreira Previdenciário"]
    result = normalize_project_name("Empresa Completamente Diferente", existing)
    assert result == "Empresa Completamente Diferente"


# ── Importer integration tests ───────────────────────────────────────────────

def _make_xlsx(rows: list[dict]) -> str:
    """Write rows to a temp .xlsx file and return the path."""
    import tempfile, os
    wb = openpyxl.Workbook()
    ws = wb.active
    headers = ["Data", "Nome", "Projeto", "Horas"]
    ws.append(headers)
    for r in rows:
        ws.append([r.get("Data"), r.get("Nome"), r.get("Projeto"), r.get("Horas")])
    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    wb.save(tmp.name)
    tmp.close()
    return tmp.name


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(
            name="Test User",
            email="test@dash.local",
            hashed_password=hash_password("dash123"),
            role="member",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        yield session, user.id


def _base_rows(n: int = 5) -> list[dict]:
    today = date.today()
    return [
        {
            "Data": (today - timedelta(days=i)).isoformat(),
            "Nome": "Test User",
            "Projeto": "Caso Silva",
            "Horas": 2.0,
        }
        for i in range(n)
    ]


def test_import_happy_path(db_session):
    session, user_id = db_session
    path = _make_xlsx(_base_rows(5))
    try:
        result = import_xlsx(path, user_id, session)
    finally:
        import os; os.unlink(path)
    assert result.imported == 5
    assert result.skipped == 0
    assert result.duplicates == 0


def test_import_skips_zero_hours(db_session):
    session, user_id = db_session
    rows = _base_rows(5)
    rows.append({
        "Data": date.today().isoformat(),
        "Nome": "Test User",
        "Projeto": "Caso Silva",
        "Horas": 0,
    })
    path = _make_xlsx(rows)
    try:
        result = import_xlsx(path, user_id, session)
    finally:
        import os; os.unlink(path)
    assert result.imported == 5
    assert result.skipped == 1


def test_import_deduplication(db_session):
    session, user_id = db_session
    rows = _base_rows(5)
    path = _make_xlsx(rows)
    try:
        first = import_xlsx(path, user_id, session)
        second = import_xlsx(path, user_id, session)
    finally:
        import os; os.unlink(path)
    assert first.imported == 5
    assert second.imported == 0
    assert second.duplicates == 5
