#!/usr/bin/env python3
"""Populate the database with test data."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from datetime import date, timedelta
import random

from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from app.models.user import User
from app.models.project import Project
from app.models.entry import TimeEntry
from app.routers.auth import hash_password

PROJECTS = [
    ("Caso Silva - Trabalhista", 40.0, 350.0),
    ("Caso Ferreira - Previdenciário", 20.0, 300.0),
    ("Acordo Coletivo 2025", 60.0, 400.0),
    ("Consultoria TechCorp", 10.0, 500.0),   # próximo do limite
    ("Revisão Contratual ABC", 8.0, 450.0),   # próximo do limite
]

ACTIVITIES = [
    "Elaboração de petição inicial",
    "Análise de documentos",
    "Audiência de instrução",
    "Reunião com cliente",
    "Pesquisa jurisprudencial",
    "Revisão de contrato",
    "Recursos e manifestações",
    "Consulta processual",
]


def run():
    create_db_and_tables()

    with Session(engine) as session:
        # Skip if already seeded
        if session.exec(select(User)).first():
            print("Database already seeded. Skipping.")
            return

        # Users
        admin = User(
            name="Admin DASH",
            email="admin@dash.local",
            hashed_password=hash_password("dash123"),
            role="admin",
            hourly_rate=400.0,
        )
        member = User(
            name="Dev Member",
            email="dev@dash.local",
            hashed_password=hash_password("dash123"),
            role="member",
            hourly_rate=300.0,
        )
        session.add(admin)
        session.add(member)
        session.commit()
        session.refresh(admin)
        session.refresh(member)

        # Projects
        projects = []
        for name, budget, rate in PROJECTS:
            p = Project(name=name.upper(), name_raw=name, budget_hours=budget, hourly_rate=rate)
            session.add(p)
        session.commit()
        projects = session.exec(select(Project)).all()

        # Time entries — 30 entries spread over last 30 days
        today = date.today()
        random.seed(42)
        for i in range(30):
            entry_date = today - timedelta(days=random.randint(0, 29))
            user = random.choice([admin, member])
            project = random.choice(projects)
            hours = round(random.uniform(0.5, 6.0), 1)
            activity = random.choice(ACTIVITIES)
            entry = TimeEntry(
                project_id=project.id,
                user_id=user.id,
                date=entry_date,
                hours=hours,
                activity=activity,
                source="chat",
                raw_input=f"{hours}h {activity.lower()} - {project.name_raw}",
                llm_confidence=round(random.uniform(0.85, 0.99), 2),
            )
            session.add(entry)

        session.commit()
        print(f"Seeded: 2 users, {len(projects)} projects, 30 time entries.")


if __name__ == "__main__":
    run()
