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

**Phase:** Not started — planning complete, no code written yet.
**Last done:** Created this plan (2026-07-06). Walkthrough confirmed by user.
**Next up:** Phase 0, step 0.1 — scaffold the repo.

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

---

## Phase 0 — Project Scaffold

Goal: empty but runnable app. `make dev` starts backend + frontend, both
respond.

- [ ] **0.1** Create repo layout:
      `backend/` (FastAPI), `frontend/` (Next.js), `docs/`, `data/`
      (SQLite DB + downloaded PDFs live here, gitignored).
- [ ] **0.2** Backend skeleton: FastAPI app with `GET /api/health`
      returning `{"status": "ok"}`. `uv` (or venv+pip) for deps.
- [ ] **0.3** Frontend skeleton: Next.js + Tailwind, one page that calls
      `/api/health` and shows the result.
- [ ] **0.4** `config.yaml` + loader: providers (anthropic/openai/gemini,
      keys from env vars) and task→model mapping (screening,
      problem_review, chat, embeddings). Validate on startup, fail with a
      clear message if a referenced env var is missing.
- [ ] **0.5** LLM adapter: one function `complete(task, messages) -> str`
      that routes through LiteLLM using the task's configured model.
      Smoke-test script proves all three providers answer "say hi".
- [ ] **0.6** `Makefile` (or `justfile`): `dev`, `test`, `lint`.
- [ ] **0.7** `.env.example`, `.gitignore` (data/, .env, node_modules,
      __pycache__), update `README.md` with setup steps.
- [ ] **0.8** First commit.

**Done when:** fresh clone + documented setup steps → both servers run,
health check green, LLM smoke test passes.

---

## Phase 1 — Data Model & Storage

Goal: the database exists and the backend can CRUD the core objects.

- [ ] **1.1** Choose migration tool (Alembic) and wire it to SQLite.
- [ ] **1.2** Tables: `project` (name, proposal_text, protocol JSON),
      `paper` (title, abstract, year, venue, authors JSON, doi, arxiv_id,
      s2_id, ntrs_id, citation_count, source, pdf_path, status:
      inbox|included|excluded|maybe), `search_query` (query text, source,
      last_run_at), `screening_decision` (paper_id, decision, reason,
      decided_by: ai|me, created_at).
- [ ] **1.3** De-duplication rule: match on DOI, else arXiv ID, else
      normalized title. Unit tests for the matcher.
- [ ] **1.4** Repository/CRUD layer + minimal API routes:
      `GET/POST /api/papers`, `PATCH /api/papers/{id}`.
- [ ] **1.5** Seed script: insert 5 hand-picked space-robotics papers so
      the UI always has something to show during development.

**Done when:** can create a project, insert papers (dupes rejected),
list/update them via API. Tests pass.

---

## Phase 2 — Project Setup & Protocol (the "first launch" flow)

Goal: paste/upload my proposal → editable protocol.

- [ ] **2.1** Upload endpoint: accept the proposal PDF, extract plain text
      (pypdf is fine here — it's my own clean PDF).
- [ ] **2.2** Protocol generation prompt: proposal text → JSON with
      research questions, keyword clusters, draft search queries.
      Save to `project.protocol`.
- [ ] **2.3** Protocol editor page: view/edit questions, keywords, queries.
      Saving re-persists; protocol is versioned (keep old copies —
      my proposal will change).
- [ ] **2.4** Manual test with the real proposal in
      `docs/Research Proposal.pdf` — sanity-check the generated protocol
      against what I know about my topic.

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
