from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.dedup import find_duplicate, normalize_arxiv_id, normalize_doi, normalize_title
from app.models import PAPER_STATUSES, Paper, Project
from app.schemas import PaperCreate, PaperOut, PaperUpdate

router = APIRouter(prefix="/api/papers", tags=["papers"])


@router.post("", response_model=PaperOut, status_code=201)
def create_paper(body: PaperCreate, db: Session = Depends(get_db)) -> Paper:
    if not db.get(Project, body.project_id):
        raise HTTPException(404, f"Project {body.project_id} not found")

    dup = find_duplicate(
        db, body.project_id, title=body.title, doi=body.doi, arxiv_id=body.arxiv_id
    )
    if dup:
        raise HTTPException(409, f"Duplicate of paper {dup.id}: {dup.title!r}")

    paper = Paper(
        **body.model_dump(exclude={"doi", "arxiv_id"}),
        doi=normalize_doi(body.doi),
        arxiv_id=normalize_arxiv_id(body.arxiv_id),
        title_normalized=normalize_title(body.title),
    )
    db.add(paper)
    db.commit()
    return paper


@router.get("", response_model=list[PaperOut])
def list_papers(
    project_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
) -> list[Paper]:
    if status is not None and status not in PAPER_STATUSES:
        raise HTTPException(422, f"status must be one of {PAPER_STATUSES}")
    query = select(Paper).order_by(Paper.id)
    if project_id is not None:
        query = query.where(Paper.project_id == project_id)
    if status is not None:
        query = query.where(Paper.status == status)
    return list(db.scalars(query))


@router.get("/{paper_id}", response_model=PaperOut)
def get_paper(paper_id: int, db: Session = Depends(get_db)) -> Paper:
    paper = db.get(Paper, paper_id)
    if not paper:
        raise HTTPException(404, f"Paper {paper_id} not found")
    return paper


@router.patch("/{paper_id}", response_model=PaperOut)
def update_paper(paper_id: int, body: PaperUpdate, db: Session = Depends(get_db)) -> Paper:
    paper = db.get(Paper, paper_id)
    if not paper:
        raise HTTPException(404, f"Paper {paper_id} not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(paper, field, value)
    db.commit()
    return paper
