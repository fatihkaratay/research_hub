def _create_project(client, name="Space Autonomy & Robotics"):
    resp = client.post("/api/projects", json={"name": name})
    assert resp.status_code == 201, resp.text
    return resp.json()


PAPER = {
    "title": "A review of space robotics technologies for on-orbit servicing",
    "abstract": "Surveys manipulation, rendezvous, and capture technologies.",
    "year": 2014,
    "venue": "Progress in Aerospace Sciences",
    "authors": ["A. Flores-Abad", "O. Ma", "K. Pham", "S. Ulrich"],
    "doi": "10.1016/j.paerosci.2014.03.002",
    "citation_count": 900,
    "source": "seed",
}


def test_project_create_and_duplicate(client):
    project = _create_project(client)
    assert project["name"] == "Space Autonomy & Robotics"
    assert client.post("/api/projects", json={"name": project["name"]}).status_code == 409


def test_paper_crud_and_dedup(client):
    project = _create_project(client)

    resp = client.post("/api/papers", json={"project_id": project["id"], **PAPER})
    assert resp.status_code == 201, resp.text
    paper = resp.json()
    assert paper["status"] == "inbox"

    # Same DOI via URL form, different title -> rejected
    dup = client.post(
        "/api/papers",
        json={
            "project_id": project["id"],
            "title": "Different title, same paper",
            "doi": "https://doi.org/10.1016/j.paerosci.2014.03.002",
        },
    )
    assert dup.status_code == 409

    # Same title with different punctuation, no DOI -> rejected
    dup2 = client.post(
        "/api/papers",
        json={
            "project_id": project["id"],
            "title": "A Review of Space Robotics Technologies for On-Orbit Servicing!",
        },
    )
    assert dup2.status_code == 409

    # List + filter
    assert len(client.get("/api/papers", params={"project_id": project["id"]}).json()) == 1
    assert (
        client.get(
            "/api/papers", params={"project_id": project["id"], "status": "included"}
        ).json()
        == []
    )

    # Update status
    patched = client.patch(f"/api/papers/{paper['id']}", json={"status": "included"})
    assert patched.status_code == 200
    assert patched.json()["status"] == "included"

    # Unknown project rejected
    assert client.post("/api/papers", json={"project_id": 999, "title": "x"}).status_code == 404
    # Bad status filter rejected
    assert client.get("/api/papers", params={"status": "bogus"}).status_code == 422
