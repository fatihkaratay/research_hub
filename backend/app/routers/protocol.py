import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pypdf import PdfReader
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Project, ProtocolVersion
from app.protocol import ProtocolError, generate_protocol, validate_protocol
from app.schemas import ProtocolOut, ProtocolPut

router = APIRouter(prefix="/api/projects/{project_id}", tags=["protocol"])


def _get_project(project_id: int, db: Session) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, f"Project {project_id} not found")
    return project


def _save_version(db: Session, project: Project, protocol: dict, source: str) -> None:
    project.protocol = protocol
    db.add(ProtocolVersion(project_id=project.id, protocol=protocol, source=source))
    db.commit()


def _protocol_out(db: Session, project: Project) -> dict:
    versions = db.scalar(
        select(func.count(ProtocolVersion.id)).where(
            ProtocolVersion.project_id == project.id
        )
    )
    return {
        "protocol": project.protocol,
        "version_count": versions or 0,
        "has_proposal": bool(project.proposal_text),
        "proposal_chars": len(project.proposal_text or ""),
    }


@router.post("/proposal", response_model=ProtocolOut)
async def upload_proposal(
    project_id: int, file: UploadFile, db: Session = Depends(get_db)
) -> dict:
    project = _get_project(project_id, db)
    payload = await file.read()

    name = (file.filename or "").lower()
    if name.endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(payload))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:  # noqa: BLE001 — surface parse failure to the client
            raise HTTPException(422, f"Could not parse PDF: {exc}") from exc
    elif name.endswith((".txt", ".md")):
        text = payload.decode("utf-8", errors="replace")
    else:
        raise HTTPException(422, "Upload a .pdf, .txt, or .md file")

    if len(text.strip()) < 200:
        raise HTTPException(
            422,
            f"Extracted only {len(text.strip())} characters — is this a scanned "
            "PDF? Try exporting the proposal as text.",
        )

    project.proposal_text = text
    db.commit()
    return _protocol_out(db, project)


@router.post("/protocol/generate", response_model=ProtocolOut)
def generate(project_id: int, db: Session = Depends(get_db)) -> dict:
    project = _get_project(project_id, db)
    if not project.proposal_text:
        raise HTTPException(409, "Upload a proposal first")
    try:
        protocol = generate_protocol(project.proposal_text)
    except ProtocolError as exc:
        raise HTTPException(502, f"Protocol generation failed: {exc}") from exc
    _save_version(db, project, protocol, source="generated")
    return _protocol_out(db, project)


@router.get("/protocol", response_model=ProtocolOut)
def get_protocol(project_id: int, db: Session = Depends(get_db)) -> dict:
    return _protocol_out(db, _get_project(project_id, db))


@router.put("/protocol", response_model=ProtocolOut)
def put_protocol(
    project_id: int, body: ProtocolPut, db: Session = Depends(get_db)
) -> dict:
    project = _get_project(project_id, db)
    try:
        protocol = validate_protocol(body.protocol)
    except ProtocolError as exc:
        raise HTTPException(422, str(exc)) from exc
    _save_version(db, project, protocol, source="edited")
    return _protocol_out(db, project)


@router.get("/protocol/versions")
def list_versions(project_id: int, db: Session = Depends(get_db)) -> list[dict]:
    _get_project(project_id, db)
    rows = db.scalars(
        select(ProtocolVersion)
        .where(ProtocolVersion.project_id == project_id)
        .order_by(ProtocolVersion.id.desc())
    )
    return [
        {
            "id": v.id,
            "source": v.source,
            "created_at": v.created_at.isoformat(),
            "protocol": v.protocol,
        }
        for v in rows
    ]
