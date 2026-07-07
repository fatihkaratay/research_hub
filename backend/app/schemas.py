"""Pydantic request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

PaperStatus = Literal["inbox", "included", "excluded", "maybe"]


class ProjectCreate(BaseModel):
    name: str


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime


class PaperCreate(BaseModel):
    project_id: int
    title: str
    abstract: str | None = None
    year: int | None = None
    venue: str | None = None
    authors: list[str] | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    s2_id: str | None = None
    ntrs_id: str | None = None
    citation_count: int | None = None
    source: str | None = None
    url: str | None = None


class PaperUpdate(BaseModel):
    status: PaperStatus | None = None
    abstract: str | None = None
    citation_count: int | None = None
    pdf_path: str | None = None


class PaperOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    abstract: str | None
    year: int | None
    venue: str | None
    authors: list[str] | None
    doi: str | None
    arxiv_id: str | None
    s2_id: str | None
    ntrs_id: str | None
    citation_count: int | None
    source: str | None
    url: str | None
    pdf_path: str | None
    status: str
    created_at: datetime
