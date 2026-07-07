from app.dedup import find_duplicate, normalize_arxiv_id, normalize_doi, normalize_title
from app.models import Paper, Project


def test_normalize_title():
    assert normalize_title("On-Orbit Servicing: A Review!") == "on orbit servicing a review"
    assert normalize_title("  Rover   Autonomy\n") == "rover autonomy"
    assert normalize_title("ROVER autonomy") == normalize_title("Rover Autonomy")


def test_normalize_doi():
    assert normalize_doi("https://doi.org/10.1016/j.paerosci.2014.03.002") == (
        "10.1016/j.paerosci.2014.03.002"
    )
    assert normalize_doi("10.1016/X") == "10.1016/x"
    assert normalize_doi(None) is None
    assert normalize_doi("  ") is None


def test_normalize_arxiv_id():
    assert normalize_arxiv_id("arXiv:2104.01234v2") == "2104.01234"
    assert normalize_arxiv_id("https://arxiv.org/abs/2104.01234") == "2104.01234"
    assert normalize_arxiv_id(None) is None


def _add_paper(db, project_id, title, doi=None, arxiv_id=None):
    paper = Paper(
        project_id=project_id,
        title=title,
        title_normalized=normalize_title(title),
        doi=normalize_doi(doi),
        arxiv_id=normalize_arxiv_id(arxiv_id),
    )
    db.add(paper)
    db.commit()
    return paper


def test_find_duplicate_by_doi(db):
    project = Project(name="p")
    db.add(project)
    db.commit()
    existing = _add_paper(db, project.id, "Some Title", doi="10.1/abc")

    hit = find_duplicate(
        db, project.id, title="Totally Different Title", doi="https://doi.org/10.1/ABC"
    )
    assert hit is not None and hit.id == existing.id


def test_find_duplicate_by_arxiv(db):
    project = Project(name="p")
    db.add(project)
    db.commit()
    existing = _add_paper(db, project.id, "Some Title", arxiv_id="2104.01234v1")

    hit = find_duplicate(
        db, project.id, title="Different", arxiv_id="arXiv:2104.01234v3"
    )
    assert hit is not None and hit.id == existing.id


def test_find_duplicate_by_normalized_title(db):
    project = Project(name="p")
    db.add(project)
    db.commit()
    existing = _add_paper(db, project.id, "On-Orbit Servicing: A Review")

    hit = find_duplicate(db, project.id, title="on orbit servicing — a review!")
    assert hit is not None and hit.id == existing.id


def test_no_false_duplicate(db):
    project = Project(name="p")
    db.add(project)
    db.commit()
    _add_paper(db, project.id, "Paper A", doi="10.1/a", arxiv_id="1111.11111")

    assert (
        find_duplicate(
            db, project.id, title="Paper B", doi="10.1/b", arxiv_id="2222.22222"
        )
        is None
    )


def test_duplicates_scoped_to_project(db):
    p1, p2 = Project(name="p1"), Project(name="p2")
    db.add_all([p1, p2])
    db.commit()
    _add_paper(db, p1.id, "Shared Title", doi="10.1/x")

    assert find_duplicate(db, p2.id, title="Shared Title", doi="10.1/x") is None
