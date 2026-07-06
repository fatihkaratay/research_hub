# Research Hub — AI-Powered Literature Review Assistant

> Brainstorm / ideas document for a web app that helps me run the literature
> review for my doctoral research. Nothing here is final — this is a working
> notebook of ideas.

## 1. Vision

A personal research workbench that takes a research question and helps me go
from **"I know nothing about this space"** to **a defensible, well-organized,
citable literature review** — while keeping me (the researcher) in control of
every judgment call.

Key principle: **AI accelerates, human decides.** The app should never invent
citations or write conclusions I haven't verified. Every AI-generated claim
must link back to a real, retrievable source.

---

## 2. The Literature Review Pipeline (and where AI helps)

A doctoral lit review is roughly a 6-stage pipeline. Each stage is a feature
area of the app:

### Stage 1 — Scoping & Question Refinement
- Chat with AI to turn a fuzzy topic into precise research questions.
- AI suggests: key terminology, synonyms, adjacent fields, seminal authors,
  and boolean search strings (for Scopus/WoS-style queries).
- Output: a **review protocol** (questions, inclusion/exclusion criteria,
  keywords) — this doubles as the PRISMA protocol if I do a systematic review.

### Stage 2 — Discovery (finding papers)
- Federated search across open APIs:
  - **Semantic Scholar API** (free, great metadata + citation graph + TLDRs)
  - **OpenAlex** (free, replacement for Microsoft Academic, huge coverage)
  - **arXiv API** (preprints, CS/physics/math)
  - **Crossref** (DOI metadata)
  - **NASA NTRS** (NASA Technical Reports Server — free API, essential for
    space autonomy/robotics: mission reports, tech memos, conference papers)
  - **CORE / Unpaywall** (open-access PDF links)
  - **IEEE Xplore** (ICRA, IROS, IEEE Aerospace — check JHU API access;
    metadata is in OpenAlex/Semantic Scholar anyway, PDFs via JHU library)
- **Citation chaining**: snowball forward (who cites this?) and backward
  (what does this cite?) from seed papers. This is where most hidden gems are.
- AI ranks results by semantic relevance to my research questions, not just
  keyword match (embeddings similarity against my protocol).

### Stage 3 — Screening (deciding what's in)
- Tinder-style screening UI: title + abstract + AI relevance rationale →
  include / exclude / maybe.
- AI pre-screens against my inclusion/exclusion criteria and explains *why*
  it recommends include/exclude — I confirm or override.
- Track everything for a **PRISMA flow diagram** (n identified, n screened,
  n excluded + reasons) — committees love this.

### Stage 4 — Deep Reading & Extraction
- Upload/fetch PDFs → parse → chunk → embed (classic RAG).
- Per-paper AI-generated **Problem Space Review** card (DECIDED — this is the
  core review schema, focused on mapping the problem space):
  - **Problem**: what specific problem are they solving, and why does it
    matter? (the gap or limitation that motivated the work)
  - **Solution & Innovation**: what approach do they propose, and what is
    genuinely new vs. prior work?
  - **Results**: what did they demonstrate? (metrics, testbeds/missions,
    sim vs. hardware, how convincing is the evaluation)
  - **Future Directions**: what do the authors say is next / unsolved?
    (this section aggregates across the corpus into a field-level
    "where is the research heading" view — key for finding my bottleneck)
  - Every field grounded with verbatim quotes + page numbers.
- **Extraction tables**: define a schema once (e.g., "sample size, country,
  method, effect size") and AI fills the table across all included papers.
  This is the single highest-value feature for a dissertation.
- Q&A over the corpus: "Which papers used mixed methods?" "Who disagrees
  with Smith 2021 and on what grounds?"

### Stage 5 — Synthesis (the actual "review")
- **Theme clustering**: embed all summaries, cluster, let AI propose theme
  labels; I rearrange in a drag-and-drop board (affinity mapping).
- **Gap analysis**: AI compares the matrix of what's been studied
  (populations × methods × contexts × variables) against my research
  questions and highlights under-explored cells → this justifies my study.
- **Contradiction detection**: surface papers with conflicting findings and
  summarize the disagreement.
- **Timeline / evolution view**: how has the conversation in this field
  evolved over decades? Who shifted the paradigm?
- Draft assistance: AI writes *per-theme* synthesis paragraphs **only from
  my included papers**, with inline citations I can verify — never from its
  training data.

### Stage 6 — Writing & Citation Management
- Export to BibTeX / RIS / CSL-JSON (Zotero-compatible).
- Citation style rendering (APA 7 etc.) via citeproc.
- Export the synthesis draft to Markdown/Word/LaTeX with a working
  bibliography.
- **Living review**: saved searches re-run weekly; new matching papers land
  in an inbox ("3 new papers match your protocol since last month").

---

## 3. How to Use AI Well (and avoid the classic failure modes)

| Risk | Mitigation |
|------|-----------|
| Hallucinated citations | AI can only cite papers that exist in my library; every claim links to a source chunk (RAG with citations). |
| Shallow summaries | Structured extraction schemas force specificity; summaries generated from full text, not abstracts alone. |
| Missing key papers | Combine keyword + semantic + citation-graph search; track "highly cited by my included set but not yet screened" papers. |
| Over-reliance / academic integrity | The app produces *drafts and evidence tables*, I write the final prose. Keep an audit log of what AI generated vs. what I wrote — useful if my committee asks. |
| Paywalled papers | Unpaywall for OA versions; otherwise store my legally obtained PDFs; never scrape publishers. |
| AI bias toward famous papers | Relevance ranking by embedding similarity to *my* protocol, with recency and citation-count as separate, visible signals I can weight. |

Prompting patterns worth building in:
- **Critic pass**: after summarizing, a second AI pass challenges the summary ("what did you miss? what's overstated?").
- **Rubric-based screening**: inclusion criteria as an explicit rubric the model scores against, with per-criterion justification.
- **Quote grounding**: every extracted claim must include a verbatim quote + page number from the PDF.

---

## 4. Architecture Sketch

```
┌─────────────┐   ┌──────────────────────────────┐
│  Next.js UI  │──▶│  API (FastAPI or Next API)   │
└─────────────┘   └──────┬───────────┬───────────┘
                          │           │
              ┌───────────▼──┐   ┌────▼─────────────┐
              │  Postgres +  │   │  Claude API       │
              │  pgvector    │   │  (summarize,      │
              │  (papers,    │   │   extract, screen,│
              │   chunks,    │   │   synthesize)     │
              │   embeddings)│   └──────────────────┘
              └───────┬──────┘
                      │
        ┌─────────────▼─────────────────┐
        │  Ingest workers                │
        │  Semantic Scholar / OpenAlex / │
        │  arXiv / Crossref / Unpaywall  │
        │  + PDF parsing (GROBID or      │
        │    unstructured / marker)      │
        └───────────────────────────────┘
```

- **Frontend**: Next.js + Tailwind (screening UI, theme board, tables).
- **Backend**: FastAPI (Python — best PDF/NLP ecosystem) or Next.js API
  routes if I want one codebase.
- **DB**: Postgres + pgvector (papers, notes, embeddings in one place).
- **PDF parsing**: GROBID (battle-tested for academic PDFs, gets sections +
  references) or `marker` / `unstructured` for simpler setup.
- **LLM**: multi-provider (DECIDED — I have API keys for Claude, OpenAI, and
  Gemini). A `config.yaml` maps each *task* to a provider/model, e.g. cheap
  fast model for screening, strongest model for deep Problem Space Reviews,
  any model for embeddings-adjacent chores. Use LiteLLM (or a thin adapter)
  so switching is a config edit, not a code change. Prompt caching + batch
  APIs where the provider supports them.
- **Embeddings**: Voyage AI (Anthropic's recommended partner) or open-source
  (e.g., `bge-m3`) if I want free/local.
- **Jobs**: background queue (Celery/RQ or simple cron) for ingest, weekly
  living-review refresh, and bulk extraction runs.

---

## 5. MVP → Full App Roadmap

**MVP (2–3 weekends)**
1. Paste a research question → boolean queries + Semantic Scholar search.
2. Screening list with AI include/exclude recommendation + rationale.
3. PDF upload → structured summary card per paper.
4. Export library to BibTeX.

**v2**
- Citation chaining (forward/backward snowball).
- Extraction tables with custom schemas.
- Corpus Q&A (RAG with quote grounding).
- PRISMA flow tracking.

**v3**
- Theme clustering + drag-and-drop synthesis board.
- Gap analysis matrix + contradiction detection.
- Per-theme draft generation with verifiable citations.
- Living review (saved searches, weekly alerts).

**Someday/maybe**
- Zotero two-way sync.
- Collaboration (share library with advisor, they comment on cards).
- Fine-grained "confidence in claim" scoring across the corpus.
- Argument graph: claims → supporting/contradicting papers, visualized.

---

## 6. Existing Tools to Learn From (and differentiate against)

- **Elicit** — great at extraction tables; closed, per-seat pricing.
- **Research Rabbit / Connected Papers / Litmaps** — citation-graph discovery.
- **Semantic Scholar** — TLDRs, citation intents (background/method/result).
- **Zotero** — reference management gold standard; integrate, don't replace.
- **scite.ai** — "smart citations" (supporting vs. contrasting).

My edge: this is **tailored to my dissertation** — my protocol, my
inclusion criteria, my extraction schema, my theoretical framework — and
everything is auditable end-to-end, which matters for a doctoral defense.

---

## 7. Decisions & Open Questions

**Decided (July 2026):**
- [x] Domain: **space autonomy & space robotics** (proposal in
      `docs/Research Proposal.pdf`, not yet finalized — still identifying
      the specific bottleneck/venue, so the app should optimize for
      *problem-space mapping*, not just summarization).
- [x] Review schema: Problem / Solution & Innovation / Results / Future
      Directions (see Stage 4).
- [x] Single user (me only) — local-first app, no auth, no multi-tenancy.
- [x] LLM budget: API keys for Claude, OpenAI, and Gemini; multi-provider
      via config file.
- [x] Review style: exploratory/scoping for now (mapping the field to find
      the bottleneck); can tighten to systematic later if the committee
      wants PRISMA rigor.

**Still open:**
- [ ] Does Johns Hopkins provide Scopus / Web of Science / IEEE Xplore API
      access? → ask the library (open APIs — Semantic Scholar, OpenAlex,
      arXiv, NTRS — are enough to start regardless).
- [ ] Which sub-area becomes the dissertation focus? (the app's
      future-directions digest should help answer this)
