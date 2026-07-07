"""Seed the DB with the project + a few real space-robotics papers so the UI
always has something to show during development. Idempotent — skips papers
that already exist (dedup).

Usage:  cd backend && .venv/bin/python scripts/seed.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.db import SessionLocal
from app.dedup import find_duplicate, normalize_doi, normalize_title
from app.models import Paper, Project

PROJECT_NAME = "Space Autonomy & Robotics"

# Hand-picked, well-known papers in the field. Metadata is approximate dev
# fixture data — real ingestion (Phase 3) pulls authoritative metadata.
PAPERS = [
    {
        "title": "A review of space robotics technologies for on-orbit servicing",
        "year": 2014,
        "venue": "Progress in Aerospace Sciences",
        "authors": ["Angel Flores-Abad", "Ou Ma", "Khanh Pham", "Steve Ulrich"],
        "doi": "10.1016/j.paerosci.2014.03.002",
        "abstract": (
            "Reviews the state of the art of space robotics for on-orbit "
            "servicing: manipulation, rendezvous, capture of non-cooperative "
            "targets, and related GNC technologies."
        ),
    },
    {
        "title": "Review of trajectory planning and control methods for free-floating space manipulators",
        "year": 2022,
        "venue": "Progress in Aerospace Sciences",
        "authors": ["(fixture)"],
        "abstract": (
            "Surveys motion planning and control for free-floating space "
            "manipulators, including dynamic coupling between base and arm."
        ),
    },
    {
        "title": "The Mars 2020 Perseverance rover mission: autonomy for surface operations",
        "year": 2021,
        "venue": "(fixture)",
        "authors": ["(fixture)"],
        "abstract": (
            "Describes autonomous capabilities used on the Perseverance rover, "
            "including enhanced AutoNav for self-driving on the Martian surface."
        ),
    },
    {
        "title": "Astrobee: a new platform for free-flying robotics on the International Space Station",
        "year": 2016,
        "venue": "i-SAIRAS",
        "authors": ["Maria Bualat", "et al."],
        "abstract": (
            "Introduces Astrobee, NASA's free-flying robot for the ISS, its "
            "hardware, software architecture, and autonomy capabilities."
        ),
    },
    {
        "title": "A survey of guidance, navigation, and control for autonomous spacecraft rendezvous and docking",
        "year": 2023,
        "venue": "(fixture)",
        "authors": ["(fixture)"],
        "abstract": (
            "Surveys GNC methods for autonomous rendezvous, proximity "
            "operations, and docking, spanning classical estimation to "
            "learning-based approaches."
        ),
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        project = db.scalar(select(Project).where(Project.name == PROJECT_NAME))
        if project is None:
            project = Project(name=PROJECT_NAME)
            db.add(project)
            db.commit()
            print(f"Created project {project.id}: {PROJECT_NAME}")
        else:
            print(f"Project exists (id={project.id})")

        added = skipped = 0
        for spec in PAPERS:
            if find_duplicate(db, project.id, title=spec["title"], doi=spec.get("doi")):
                skipped += 1
                continue
            db.add(
                Paper(
                    project_id=project.id,
                    title_normalized=normalize_title(spec["title"]),
                    **{**spec, "doi": normalize_doi(spec.get("doi"))},
                    source="seed",
                )
            )
            added += 1
        db.commit()
        print(f"Papers: {added} added, {skipped} already present")
    finally:
        db.close()


if __name__ == "__main__":
    main()
