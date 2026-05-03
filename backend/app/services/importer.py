from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date

import pandas as pd
from sqlmodel import Session, select

from ..config import settings
from ..models.entry import TimeEntry
from ..models.project import Project
from .normalizer import normalize_project_name


@dataclass
class ImportResult:
    imported: int = 0
    skipped: int = 0
    duplicates: int = 0
    warnings: list[str] = field(default_factory=list)


def _best_sheet(xlsx_path: str) -> pd.DataFrame:
    xl = pd.ExcelFile(xlsx_path, engine="openpyxl")
    best, best_len = None, -1
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        if len(df) > best_len:
            best, best_len = df, len(df)
    return best if best is not None else pd.DataFrame()


def _validate_columns(df: pd.DataFrame, mapping: dict) -> list[str]:
    required = set(mapping.values())
    missing = required - set(df.columns)
    return list(missing)


def _clean(df: pd.DataFrame, col_hours: str) -> tuple[pd.DataFrame, int]:
    before = len(df)
    df = df.copy()
    df[col_hours] = pd.to_numeric(df[col_hours], errors="coerce")
    df = df[df[col_hours].notna() & (df[col_hours] != 0)]
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
    skipped = before - len(df)
    return df.reset_index(drop=True), skipped


def _to_date(val) -> date | None:
    try:
        return pd.to_datetime(val).date()
    except Exception:
        return None


def import_xlsx(file_path: str, user_id: int, db: Session) -> ImportResult:
    result = ImportResult()
    mapping = settings.COLUMN_MAPPING
    col_date = mapping["data"]
    col_project = mapping["projeto"]
    col_hours = mapping["horas"]

    df = _best_sheet(file_path)
    if df.empty:
        result.warnings.append("Arquivo sem dados.")
        return result

    missing = _validate_columns(df, mapping)
    if missing:
        result.warnings.append(f"Colunas obrigatórias ausentes: {missing}")
        return result

    df, skipped = _clean(df, col_hours)
    result.skipped += skipped

    existing_projects = db.exec(select(Project)).all()
    existing_names = [p.name for p in existing_projects]
    project_cache: dict[str, int] = {p.name: p.id for p in existing_projects}

    for raw_name in df[col_project].unique():
        normalized = normalize_project_name(raw_name, existing_names)
        if normalized not in project_cache:
            new_proj = Project(name=normalized, name_raw=raw_name)
            db.add(new_proj)
            db.commit()
            db.refresh(new_proj)
            project_cache[normalized] = new_proj.id
            existing_names.append(normalized)

    existing_keys: set[tuple] = set()
    existing_entries = db.exec(
        select(TimeEntry).where(TimeEntry.user_id == user_id)
    ).all()
    for e in existing_entries:
        existing_keys.add((user_id, e.project_id, e.date, e.hours))

    batch: list[TimeEntry] = []

    for _, row in df.iterrows():
        entry_date = _to_date(row[col_date])
        if entry_date is None:
            result.skipped += 1
            result.warnings.append(f"Data inválida ignorada: {row[col_date]}")
            continue

        hours = float(row[col_hours])
        raw_name = str(row[col_project])
        normalized = normalize_project_name(raw_name, existing_names)
        project_id = project_cache[normalized]

        key = (user_id, project_id, entry_date, hours)
        if key in existing_keys:
            result.duplicates += 1
            continue

        existing_keys.add(key)
        entry = TimeEntry(
            project_id=project_id,
            user_id=user_id,
            date=entry_date,
            hours=hours,
            activity=None,
            source="excel",
            raw_input=str(row.to_dict()),
        )
        batch.append(entry)

        if len(batch) >= 100:
            db.add_all(batch)
            db.commit()
            result.imported += len(batch)
            batch = []

    if batch:
        db.add_all(batch)
        db.commit()
        result.imported += len(batch)

    return result
