# Research Hub — Implementation Plan & Progress Tracker

> **How to use this file (for Claude and for me):**
> This is the single source of truth for build progress. At the start of
> every session, read this file top to bottom before writing any code.
> - **Current Status** below says exactly where we left off.
> - Check off items (`[x]`) the moment they are done and verified.
> - After each working session, update **Current Status** and add a line to
>   the **Session Log** at the bottom (date, what was done, what's next).
> - If a decision changes (stack, schema, scope), record it in
>   **Decision Log** so we never re-litigate it.
>
> Related docs: `IDEAS.md` (concepts & features), `WALKTHROUGH.md`
> (confirmed user experience — build to match this).

---

## Current Status

**Phase:** Phase 2 COMPLETE. ✅ (Phases 0–2 done)
**Last done:** Proposal upload (.pdf/.txt/.md → text), LLM protocol
generation (validated JSON: research_questions / keyword_clusters /
queries), versioned protocol storage (protocol_version table), protocol
editor page at /protocol. Tested live with the real proposal: 19,762 chars
extracted, Gemini generated 5 RQs / 6 clusters / 10 queries — all
on-topic (GNN warm-starts for decentralized multi-robot trajectory
optimization). Survives backend restart. 14 tests green.
**Next up:** Phase 3, step 3.1 — Semantic Scholar search client.

---

## Decision Log

| Date | Decision |
|------|----------|
| 2026-07-06 | Domain: space autonomy & space robotics. Exploratory/scoping review to find dissertation bottleneck. |
| 2026-07-06 | Review card schema: Problem / Solution & Innovation / Results / Future Directions, quote-grounded. |
| 2026-07-06 | Single user, local-first. No auth, no multi-tenancy. |
| 2026-07-06 | Multi-provider LLM (Claude + OpenAI + Gemini keys available) via `config.yaml`, LiteLLM as the adapter. |
| 2026-07-06 | Stack: **FastAPI (Python) backend + Next.js frontend + SQLite** (with `sqlite-vec` for embeddings). SQLite over Postgres because single-user/local — zero setup, one file to back up. Revisit only if it actually hurts. |
| 2026-07-06 | Sources for MVP: Semantic Scholar first, then arXiv + NASA NTRS. OpenAlex in v2. Scopus/WoS pending JHU library answer. |
| 2026-07-06 | TEMPORARY: all tasks routed to `gemini/gemini-2.5-flash` (free tier; `gemini-2.5-pro` has free-tier limit 0). Claude routing preserved as comments in config.yaml — swap back when the Anthropic key arrives. OpenAI key present but $0 API credit. |
| 2026-07-06 | TLS: this machine's shell sets SSL_CERT_FILE to a JHUAPL-only root CA, breaking Python HTTPS to public sites. `backend/app/__init__.py` builds a combined certifi+JHUAPL bundle in `data/ca-bundle.pem` and points the process at it. Don't remove. |

---

## Phase 0 — Project Scaffold

Goal: empty but runnable app. `make dev` starts backend + frontend, both
respond.

- [x] **0.1** Create repo layout:
      `backend/` (FastAPI), `frontend/` (Next.js), `docs/`, `data/`
      (SQLite DB + downloaded PDFs live here, gitignored).
- [x] **0.2** Backend skeleton: FastAPI app with `GET /api/health`
      returning `{"status": "ok"}`. venv+pip for deps (no uv on machine).
- [x] **0.3** Frontend skeleton: Next.js 16 + Tailwind, home page calls
      `/api/health` (proxied via next.config rewrite) and shows the result.
- [x] **0.4** `config.yaml` + loader: providers (anthropic/openai/gemini,
      keys from env vars) and task→model mapping (screening,
      problem_review, protocol, corpus_synthesis, chat). *Deviation from
      plan: missing keys are a startup warning + surfaced in `/api/health`,
      and a hard error only when the task is actually invoked — so the app
      runs without keys.* Models: haiku-4-5 for screening, opus-4-8 for
      deep tasks (embeddings task deferred to Phase 6 when it's needed).
- [x] **0.5** LLM adapter `complete(task, messages)` via LiteLLM +
      `scripts/smoke_test.py`. Verified live on Gemini (2026-07-06): all
      task routes answer. OpenAI key valid but $0 quota; Anthropic key
      not yet created.
- [x] **0.6** `Makefile`: `dev`, `dev-backend`, `dev-frontend`, `test`,
      `lint`, `smoke`.
- [x] **0.7** `.env.example`, `.gitignore` extended (data/, node_modules,
      .next), `README.md` rewritten with setup steps.
- [x] **0.8** First commit.

**Done when:** fresh clone + documented setup steps → both servers run,
health check green, LLM smoke test passes.

---

## Phase 1 — Data Model & Storage

Goal: the database exists and the backend can CRUD the core objects.

- [x] **1.1** Alembic wired to SQLite (`data/research_hub.db`); initial
      migration `5a8685c38c5a` applied. `RESEARCH_HUB_DB` env var overrides
      the DB URL (tests use in-memory).
- [x] **1.2** Tables: `project`, `paper` (incl. `title_normalized` dedup
      key + url field), `search_query`, `screening_decision` — as planned.
- [x] **1.3** Dedup in `app/dedup.py`: DOI (URL-form + case normalized) →
      arXiv ID (prefix/version stripped) → normalized title; scoped per
      project. 6 unit tests.
- [x] **1.4** Routes: `GET/POST /api/projects`, `GET/POST /api/papers`
      (+ `GET/PATCH /api/papers/{id}`); duplicates → 409. 4 API tests via
      dependency-override in-memory DB.
- [x] **1.5** `scripts/seed.py` — idempotent, 5 hand-picked papers
      (fixture-grade metadata; real ingestion replaces it in Phase 3).

**Done when:** can create a project, insert papers (dupes rejected),
list/update them via API. Tests pass.

---

## Phase 2 — Project Setup & Protocol (the "first launch" flow)

Goal: paste/upload my proposal → editable protocol.

- [x] **2.1** `POST /api/projects/{id}/proposal` — accepts .pdf/.txt/.md,
      extracts text (pypdf), rejects scans (<200 chars extracted).
- [x] **2.2** `POST /api/projects/{id}/protocol/generate` — LLM ("protocol"
      task) → validated JSON, saved to `project.protocol`.
- [x] **2.3** Protocol editor at `/protocol`: upload, generate, edit
      questions/clusters/queries, save. Every generate/save appends to
      `protocol_version` (`GET .../protocol/versions`).
- [x] **2.4** Manual test with real proposal: 19,762 chars extracted;
      Gemini produced 5 RQs, 6 keyword clusters, 10 queries — accurately
      reflecting the proposal (GNN warm-starts, decentralized multi-robot
      trajectory optimization, sim-to-real, safety/verification).

**Done when:** I can upload the proposal, get a sensible protocol, edit it,
and it survives restart.

---

## Phase 3 — Discovery (search & ingest)

Goal: saved queries fill the inbox with de-duplicated candidate papers.

- [ ] **3.1** Semantic Scholar client: search endpoint, map response →
      `paper` rows. Respect rate limits (no API key tier: be polite,
      backoff on 429).
- [ ] **3.2** arXiv client (Atom API), same mapping.
- [ ] **3.3** NASA NTRS client (`ntrs.nasa.gov` API), same mapping.
- [ ] **3.4** "Run searches" action: execute all protocol queries against
      all sources, de-dupe, insert new papers as `inbox`. Show per-source
      counts (found / new / duplicate).
- [ ] **3.5** Relevance scoring: for each new inbox paper, cheap-model call
      scoring title+abstract against the protocol → one-line relevance
      note + 0–100 score, stored on the paper.
- [ ] **3.6** Inbox page: table of inbox papers (title, venue, year,
      citations, relevance note), sortable by score/year/citations.

**Done when:** clicking "Run searches" on my real protocol yields a ranked
inbox of real papers from all three sources with no duplicates.

---

## Phase 4 — Screening

Goal: the 20-minutes-with-coffee flow from the walkthrough.

- [ ] **4.1** AI screening recommendation: per paper, include/exclude/
      unsure + reasoning against protocol criteria (stored as a
      `screening_decision` with `decided_by=ai`).
- [ ] **4.2** Screening page: one paper at a time — title, abstract, AI
      recommendation + reasoning. Buttons and keyboard shortcuts:
      `i` include, `x` exclude, `m` maybe, `space`/`→` next.
- [ ] **4.3** My decision recorded as `decided_by=me` (AI rec is kept
      separately — never overwritten, so I can audit agreement later).
- [ ] **4.4** Counters for PRISMA-style bookkeeping: identified / screened /
      included / excluded (+ exclusion reasons). Simple stats endpoint +
      display.
- [ ] **4.5** Undo (`u`) — mis-keying at speed is guaranteed.

**Done when:** I can screen 20 real papers start-to-finish with keyboard
only, and the counts add up.

---

## Phase 5 — PDFs & the Problem Space Review

Goal: the heart of the app — the quote-grounded review card.

- [ ] **5.1** PDF fetch for included papers: try arXiv → NTRS → Unpaywall;
      store under `data/pdfs/`; mark `needs_manual_upload` when all fail.
- [ ] **5.2** Manual PDF upload (for papers I fetch via JHU library).
- [ ] **5.3** PDF → text with page mapping. Start with `pymupdf` (fitz):
      extract text per page, keep page numbers. (GROBID postponed —
      revisit only if extraction quality blocks us. Note: two-column
      IEEE/AIAA layouts are the risk; test on 3 real papers early.)
- [ ] **5.4** Problem Space Review generation: strong-model call with full
      paper text → JSON: `problem`, `solution_innovation`, `results`,
      `future_directions`, each a list of bullets with
      `{claim, quote, page}`. Store as `review` table row.
- [ ] **5.5** Validation pass: verify each `quote` actually appears on the
      claimed page (fuzzy match); flag bullets that fail as unverified.
- [ ] **5.6** Paper detail page: PDF viewer left (pdf.js), review card
      right; clicking a claim jumps the viewer to that page.
- [ ] **5.7** My layer on top: free-text notes + tags + "relevance to my
      RQs" rating (1–5) on each paper.
- [ ] **5.8** Batch action: "review all included papers without a card"
      with progress display and cost estimate before running.

**Done when:** for 5 real papers, cards are generated, quotes verify, and
click-to-page works.

---

## Phase 6 — Corpus Views (the payoff)

Goal: field-level insight — where's my bottleneck?

- [ ] **6.1** Embeddings: embed review bullets (per section) via configured
      embedding model, store in `sqlite-vec`.
- [ ] **6.2** Problem Map: cluster `problem` bullets; AI labels each
      cluster; page shows clusters sized by paper count, each expandable
      to its papers. Crowded vs. thin is visible at a glance.
- [ ] **6.3** "Where the Field Is Heading": cluster `future_directions`
      bullets across corpus, ranked by # of distinct papers pointing at
      each cluster; every cluster links back to sources.
- [ ] **6.4** Innovation Timeline: papers by year, colored by method class /
      validation level (sim / hardware / flight) — needs those two fields
      added to the review schema or extraction table first.
- [ ] **6.5** Extraction table: define column schema in UI → batch model
      run fills cells (each with source quote) → sortable table → CSV
      export.
- [ ] **6.6** Corpus chat: question → retrieve relevant chunks across all
      included papers → answer with paper + page citations.

**Done when:** with 30+ reviewed papers, the Problem Map and Future
Directions views produce clusters I actually find informative (subjective —
I judge).

---

## Phase 7 — Living Review & Export

- [ ] **7.1** "Refresh searches" surfaces only *new* papers since last run;
      inbox badge shows count. (Scheduling can just be me clicking a
      button weekly, or a cron/launchd job later.)
- [ ] **7.2** Export BibTeX + RIS for included papers.
- [ ] **7.3** Export review cards + my notes to Markdown (one file per
      paper, or one big file per tag).
- [ ] **7.4** Export per-cluster synthesis draft (Markdown, citations only
      from library) — clearly labeled as AI draft.
- [ ] **7.5** Backup story: one command zips `data/` (DB + PDFs).

---

## Later / Ideas Parking Lot

- OpenAlex as fourth source; Scopus/WoS if JHU access confirmed.
- Citation chaining (forward/backward snowball from included papers).
- Zotero sync. GROBID for better PDF parsing. Contradiction detection.
- Model comparison mode (same paper, two providers, diff the cards).

---

## Session Log

| Date | What happened | Next |
|------|--------------|------|
| 2026-07-06 | Wrote IDEAS.md, WALKTHROUGH.md (user confirmed), this plan. No code yet. | Phase 0: scaffold repo. |
| 2026-07-06 | Phase 0 done: FastAPI backend + Next.js 16 frontend + config.yaml/LiteLLM adapter + Makefile. Verified health check end-to-end through the :3000→:8000 proxy. Smoke test pending API keys. | User: fill `.env`, run `make smoke`. Then Phase 1 (SQLite + Alembic + paper tables). |
| 2026-07-06 | OpenAI-only testing: routed all tasks to gpt-5/gpt-5-mini, smoke test skips keyless providers, fixed JHUAPL SSL_CERT_FILE breaking Python HTTPS (combined CA bundle). Key authenticates; completions blocked by $0 OpenAI quota. | User: add OpenAI API credit, run `make smoke`. Then Phase 1. |
| 2026-07-06 | Gemini free-tier key added. All tasks → gemini-2.5-flash (pro has free-tier limit 0). Verified live: smoke test OK + all `complete()` task routes answer. **Phase 0 closed.** | Phase 1: SQLite + Alembic + paper/project/decision tables. |
| 2026-07-07 | Phase 1 done: SQLAlchemy models + Alembic migration, dedup module, projects/papers CRUD API, 10 tests green, seed script (idempotent). Live-verified: duplicate insert → 409, patch status works. **Phase 1 closed.** | Phase 2: proposal upload → protocol generation → protocol editor. |
| 2026-07-07 | Phase 2 done: proposal upload, protocol generation (live-tested with real proposal — output on-topic), versioned protocol storage, /protocol editor page. 14 tests green. **Phase 2 closed.** | Phase 3: discovery — Semantic Scholar, arXiv, NTRS clients → inbox. |
