from sqlmodel import SQLModel, Session, create_engine
from .config import settings

_url = settings.DATABASE_URL

if _url.startswith("postgresql"):
    engine = create_engine(_url, echo=settings.DEBUG)
else:
    engine = create_engine(
        _url,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
    )


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
