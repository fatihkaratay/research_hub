"""Duplicate detection for incoming papers.

Match order: DOI, else arXiv ID, else normalized title. All comparisons are
scoped to a project.
"""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Paper


def normalize_title(title: str) -> str:
    """Lowercase, drop everything but letters/digits, collapse whitespace."""
    cleaned = re.sub(r"[^a-z0-9]+", " ", title.lower())
    return " ".join(cleaned.split())


def normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = doi.strip().lower()
    # Strip common URL prefixes so "https://doi.org/10.x/y" == "10.x/y"
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    return doi or None


def normalize_arxiv_id(arxiv_id: str | None) -> str | None:
    if not arxiv_id:
        return None
    arxiv_id = arxiv_id.strip().lower()
    arxiv_id = re.sub(r"^(https?://arxiv\.org/(abs|pdf)/|arxiv:)", "", arxiv_id)
    # Drop version suffix: 2104.01234v2 -> 2104.01234
    arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
    return arxiv_id or None


def find_duplicate(
    db: Session,
    project_id: int,
    *,
    title: str,
    doi: str | None = None,
    arxiv_id: str | None = None,
) -> Paper | None:
    """Return the existing paper this candidate duplicates, if any."""
    doi = normalize_doi(doi)
    if doi:
        hit = db.scalar(
            select(Paper).where(Paper.project_id == project_id, Paper.doi == doi)
        )
        if hit:
            return hit

    arxiv_id = normalize_arxiv_id(arxiv_id)
    if arxiv_id:
        hit = db.scalar(
            select(Paper).where(Paper.project_id == project_id, Paper.arxiv_id == arxiv_id)
        )
        if hit:
            return hit

    return db.scalar(
        select(Paper).where(
            Paper.project_id == project_id,
            Paper.title_normalized == normalize_title(title),
        )
    )
