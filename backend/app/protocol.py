"""Generate a review protocol (research questions, keywords, queries) from
the research proposal text, and validate protocol JSON coming from the LLM
or the editor UI."""

from __future__ import annotations

import json
import re

from app.llm import complete

GENERATION_PROMPT = """\
You are helping a doctoral researcher set up a literature review protocol.
Their research area is space autonomy and space robotics. Their research
proposal is below. It is NOT final — they are still mapping the problem
space to find the specific bottleneck their dissertation will address, so
favor breadth over premature narrowing.

From the proposal, produce a literature review protocol as JSON with exactly
this shape:

{
  "research_questions": ["...", ...],          // 3-6 precise questions the review must answer
  "keyword_clusters": [                        // 4-8 clusters of related terms
    {"name": "cluster name", "keywords": ["term", "synonym", ...]},
    ...
  ],
  "queries": ["...", ...]                      // 5-10 search strings for academic search engines
}

Guidance:
- keyword_clusters should cover the proposal's core topics AND adjacent
  areas a thorough review of this field needs (e.g. verification of
  autonomy, fault management, sim-to-real transfer) when the proposal
  touches them.
- queries should be plain keyword search strings (2-6 terms, optionally
  quoted phrases). They will run against Semantic Scholar, arXiv, and NASA
  NTRS — no field tags, no Scopus/WoS syntax.

Return ONLY the JSON object, no other text.

PROPOSAL:
---
{proposal}
---
"""


class ProtocolError(ValueError):
    pass


def validate_protocol(data: dict) -> dict:
    """Check shape; return a cleaned copy. Raises ProtocolError."""
    if not isinstance(data, dict):
        raise ProtocolError("protocol must be a JSON object")

    questions = data.get("research_questions")
    clusters = data.get("keyword_clusters")
    queries = data.get("queries")

    if not isinstance(questions, list) or not all(isinstance(q, str) and q.strip() for q in questions):
        raise ProtocolError("research_questions must be a list of non-empty strings")
    if not isinstance(queries, list) or not all(isinstance(q, str) and q.strip() for q in queries):
        raise ProtocolError("queries must be a list of non-empty strings")
    if not isinstance(clusters, list):
        raise ProtocolError("keyword_clusters must be a list")
    cleaned_clusters = []
    for c in clusters:
        if (
            not isinstance(c, dict)
            or not isinstance(c.get("name"), str)
            or not isinstance(c.get("keywords"), list)
            or not all(isinstance(k, str) and k.strip() for k in c["keywords"])
        ):
            raise ProtocolError(
                "each keyword_cluster must be {name: str, keywords: [str, ...]}"
            )
        cleaned_clusters.append(
            {"name": c["name"].strip(), "keywords": [k.strip() for k in c["keywords"]]}
        )

    return {
        "research_questions": [q.strip() for q in questions],
        "keyword_clusters": cleaned_clusters,
        "queries": [q.strip() for q in queries],
    }


def parse_llm_json(text: str) -> dict:
    """Parse JSON from an LLM response, tolerating markdown fences."""
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProtocolError(f"LLM did not return valid JSON: {exc}") from exc


def generate_protocol(proposal_text: str) -> dict:
    prompt = GENERATION_PROMPT.replace("{proposal}", proposal_text)
    raw = complete("protocol", [{"role": "user", "content": prompt}])
    return validate_protocol(parse_llm_json(raw))
