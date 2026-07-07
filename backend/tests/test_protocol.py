import pytest

from app.protocol import ProtocolError, parse_llm_json, validate_protocol

GOOD = {
    "research_questions": ["What autonomy levels have flown?"],
    "keyword_clusters": [{"name": "rendezvous", "keywords": ["docking", "proximity ops"]}],
    "queries": ["autonomous spacecraft docking"],
}


def test_validate_good():
    out = validate_protocol(GOOD)
    assert out["research_questions"] == GOOD["research_questions"]
    assert out["keyword_clusters"][0]["keywords"] == ["docking", "proximity ops"]


def test_validate_rejects_bad_shapes():
    with pytest.raises(ProtocolError):
        validate_protocol({**GOOD, "research_questions": "not a list"})
    with pytest.raises(ProtocolError):
        validate_protocol({**GOOD, "keyword_clusters": [{"name": "x"}]})  # no keywords
    with pytest.raises(ProtocolError):
        validate_protocol({**GOOD, "queries": [""]})
    with pytest.raises(ProtocolError):
        validate_protocol([])


def test_parse_llm_json_plain_and_fenced():
    assert parse_llm_json('{"a": 1}') == {"a": 1}
    assert parse_llm_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_llm_json('Sure!\n```\n{"a": 1}\n```') == {"a": 1}
    with pytest.raises(ProtocolError):
        parse_llm_json("I cannot do that")


def test_protocol_api_flow(client, monkeypatch):
    project = client.post("/api/projects", json={"name": "p"}).json()
    pid = project["id"]

    # Generate before proposal -> 409
    assert client.post(f"/api/projects/{pid}/protocol/generate").status_code == 409

    # Upload a .txt proposal (PDF path exercised manually with the real file)
    text = ("Space autonomy research proposal. " * 20).encode()
    resp = client.post(
        f"/api/projects/{pid}/proposal",
        files={"file": ("proposal.txt", text, "text/plain")},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["has_proposal"] is True

    # Too-short upload rejected
    short = client.post(
        f"/api/projects/{pid}/proposal",
        files={"file": ("tiny.txt", b"hello", "text/plain")},
    )
    assert short.status_code == 422

    # Generate with mocked LLM
    monkeypatch.setattr(
        "app.protocol.complete",
        lambda task, messages, **kw: '```json\n'
        '{"research_questions": ["RQ1"],'
        ' "keyword_clusters": [{"name": "c", "keywords": ["k1"]}],'
        ' "queries": ["q1"]}\n```',
    )
    gen = client.post(f"/api/projects/{pid}/protocol/generate")
    assert gen.status_code == 200, gen.text
    assert gen.json()["protocol"]["research_questions"] == ["RQ1"]
    assert gen.json()["version_count"] == 1

    # Edit and save -> new version
    edited = gen.json()["protocol"]
    edited["research_questions"].append("RQ2 (mine)")
    put = client.put(f"/api/projects/{pid}/protocol", json={"protocol": edited})
    assert put.status_code == 200
    assert put.json()["version_count"] == 2

    # Invalid edit rejected
    bad = client.put(
        f"/api/projects/{pid}/protocol", json={"protocol": {"research_questions": [1]}}
    )
    assert bad.status_code == 422

    # Current protocol + versions
    cur = client.get(f"/api/projects/{pid}/protocol").json()
    assert "RQ2 (mine)" in cur["protocol"]["research_questions"]
    versions = client.get(f"/api/projects/{pid}/protocol/versions").json()
    assert [v["source"] for v in versions] == ["edited", "generated"]
