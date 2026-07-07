"""Database engine and session management (SQLite, single user)."""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import REPO_ROOT

DATA_DIR = REPO_ROOT / "data"
DATABASE_URL = os.environ.get("RESEARCH_HUB_DB", f"sqlite:///{DATA_DIR / 'research_hub.db'}")


class Base(DeclarativeBase):
    pass


def make_engine(url: str = DATABASE_URL):
    if url.startswith("sqlite:///") and ":memory:" not in url:
        DATA_DIR.mkdir(exist_ok=True)
    return create_engine(url, connect_args={"check_same_thread": False})


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    """FastAPI dependency — one session per request."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
