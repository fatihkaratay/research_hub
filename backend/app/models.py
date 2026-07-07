"""SQLAlchemy models: project, paper, search_query, screening_decision."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

# Paper lifecycle: discovered -> screened -> (included | excluded | maybe)
PAPER_STATUSES = ("inbox", "included", "excluded", "maybe")
DECISIONS = ("include", "exclude", "maybe", "unsure")
DECIDED_BY = ("ai", "me")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "project"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    proposal_text: Mapped[str | None] = mapped_column(Text)
    protocol: Mapped[dict | None] = mapped_column(JSON)  # questions/keywords/queries
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    papers: Mapped[list[Paper]] = relationship(back_populates="project")


class Paper(Base):
    __tablename__ = "paper"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    title: Mapped[str]
    title_normalized: Mapped[str] = mapped_column(index=True)  # dedup key
    abstract: Mapped[str | None] = mapped_column(Text)
    year: Mapped[int | None]
    venue: Mapped[str | None]
    authors: Mapped[list | None] = mapped_column(JSON)  # ["A. Author", ...]
    doi: Mapped[str | None] = mapped_column(index=True)
    arxiv_id: Mapped[str | None] = mapped_column(index=True)
    s2_id: Mapped[str | None]  # Semantic Scholar paper id
    ntrs_id: Mapped[str | None]  # NASA NTRS record id
    citation_count: Mapped[int | None]
    source: Mapped[str | None]  # where we first found it
    url: Mapped[str | None]
    pdf_path: Mapped[str | None]  # relative to data/, set once fetched
    status: Mapped[str] = mapped_column(default="inbox")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    project: Mapped[Project] = relationship(back_populates="papers")
    decisions: Mapped[list[ScreeningDecision]] = relationship(back_populates="paper")

    __table_args__ = (Index("ix_paper_project_status", "project_id", "status"),)


class ProtocolVersion(Base):
    """History of the review protocol — the proposal will change, keep every
    version. `project.protocol` always holds the current one."""

    __tablename__ = "protocol_version"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), index=True)
    protocol: Mapped[dict] = mapped_column(JSON)
    source: Mapped[str]  # generated | edited
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class SearchQuery(Base):
    __tablename__ = "search_query"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    query: Mapped[str]
    source: Mapped[str]  # semantic_scholar | arxiv | ntrs
    last_run_at: Mapped[datetime | None]


class ScreeningDecision(Base):
    __tablename__ = "screening_decision"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("paper.id"), index=True)
    decision: Mapped[str]  # include | exclude | maybe | unsure
    reason: Mapped[str | None] = mapped_column(Text)
    decided_by: Mapped[str]  # ai | me  (AI recs kept forever, never overwritten)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    paper: Mapped[Paper] = relationship(back_populates="decisions")
