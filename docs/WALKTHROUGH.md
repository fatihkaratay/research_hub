# Research Hub — User Walkthrough

What using the app feels like, written as a day-in-the-life. Single user
(me), domain: space autonomy & space robotics, phase: exploratory — I'm
mapping the problem space to find my dissertation bottleneck.

---

## First launch — Project setup (once)

I run `research-hub` and open `localhost:3000`. The app asks me to create a
**project**: I name it *"Space Autonomy & Robotics"* and drop in my research
proposal PDF plus a few sentences about what I care about.

The app reads the proposal and proposes back:

- a set of **candidate research questions** it detected,
- a **keyword map** (e.g., autonomous rendezvous & docking, on-orbit
  servicing, planetary rover autonomy, fault detection & recovery,
  vision-based navigation, multi-agent spacecraft…),
- draft **search queries** per keyword cluster.

I edit these — delete what's off-base, add terms it missed. This becomes my
**review protocol**, and everything downstream is measured against it. I can
revise it anytime (important, since my proposal isn't finalized).

## Morning — Discovery inbox

The home screen is an **inbox of candidate papers**. Overnight, the app ran
my saved queries against Semantic Scholar, OpenAlex, arXiv, and NASA NTRS,
de-duplicated by DOI/title, and pulled metadata + abstracts.

Each row shows: title, venue, year, citation count, and an **AI relevance
note** — one sentence on why this matches (or doesn't match) my protocol,
scored by the cheap model from my `config.yaml`.

## Screening — 20 minutes with coffee

I hit "Screen" and get one paper at a time: title, abstract, the AI's
include/exclude recommendation *with its reasoning against my criteria*.

Keyboard shortcuts: `i` include, `x` exclude, `m` maybe, `space` next.
I can burn through 50 papers in 20 minutes because I'm reviewing the AI's
judgment, not reading cold. Every decision is logged (count of
identified/screened/excluded + reasons), so if I later formalize this into
a systematic review chapter, the PRISMA numbers already exist.

Included papers move to my **Library** and the app tries to fetch the PDF
(arXiv, NTRS, Unpaywall; otherwise it flags "upload manually" and I grab it
via JHU library access).

## Deep dive — the Problem Space Review

I open a paper in the Library. Left pane: the PDF. Right pane: the
**Problem Space Review** card the strong model generated from the full text:

> **Problem** — What specific problem are they solving? Why does it matter?
> What limitation of prior work motivated this?
>
> **Solution & Innovation** — The proposed approach, and what's genuinely
> new versus what's borrowed from prior work.
>
> **Results** — What they demonstrated: metrics, sim vs. hardware vs.
> flight, testbed details, how convincing the evaluation is.
>
> **Future Directions** — What the authors say is unsolved or next.

Every bullet has a superscript link; clicking it jumps the PDF pane to the
exact quote and page. If the card claims "validated on hardware" I can
verify in five seconds that it wasn't just a Gazebo sim.

Below the card: my own notes field, tags (e.g., `#rover`, `#FDIR`,
`#learning-based`, `#flight-heritage`), and a "relates to my RQs" rating.

I can also chat with the paper: "Did they consider communication delay?"
"What assumptions does their fault model make?" — answers cite page numbers.

## The payoff — corpus-level views

Once ~30+ papers are reviewed, the tabs that matter for *me* light up:

**Problem Map** — clusters of the *Problem* fields across all papers, so I
see the field's actual problem taxonomy: which problems are crowded (20
papers on vision-based relative navigation) and which are thin (2 papers on
autonomy verification for long-duration missions). Crowded = hard to
contribute; thin = potential bottleneck worth my dissertation.

**Where the Field Is Heading** — an aggregated digest of every paper's
*Future Directions*, clustered and ranked by how many authors independently
point at the same open problem. This is literally the "what should I work
on" view. Each cluster links back to the papers that mention it.

**Innovation Timeline** — solutions plotted by year: when did the field
shift from classical estimation to learning-based methods? What has actually
flown vs. stayed in simulation? (The sim-to-flight gap is itself a classic
space-robotics bottleneck signal.)

**Extraction Table** — a spreadsheet I define once (e.g., columns:
*platform, autonomy level, method class, validation environment, TRL*) and
the model fills across the corpus. Sortable, exportable to CSV, and every
cell links to its source quote.

## Ongoing — the living review

Every week the app re-runs my queries and the inbox shows "7 new papers
match your protocol." Ten minutes of screening keeps the review current
through my entire PhD — no more "my lit review was current two years ago"
panic before the defense.

## Getting it out

- **Export → BibTeX/RIS** for Zotero/LaTeX.
- **Export → Review draft**: per-cluster synthesis paragraphs in Markdown,
  citing only papers in my library, which I then rewrite in my own voice.
- **Export → Extraction table** as CSV for the dissertation appendix.

---

## The multi-provider config (`config.yaml`)

```yaml
providers:
  anthropic: { api_key_env: ANTHROPIC_API_KEY }
  openai:    { api_key_env: OPENAI_API_KEY }
  gemini:    { api_key_env: GEMINI_API_KEY }

tasks:
  screening:        { model: claude-haiku-4-5 }      # cheap, high volume
  problem_review:   { model: claude-fable-5 }        # deep, per-paper
  corpus_synthesis: { model: claude-fable-5 }        # clustering labels, digests
  chat:             { model: gpt-5 }                 # or whatever I feel like
  embeddings:       { model: gemini-embedding }      # or voyage / local
```

Swapping models = editing one line. Useful for comparing providers on the
same paper, and for keeping the bulk work on cheap models.

---

## What the app deliberately does NOT do

- Write my literature review chapter for me (drafts + evidence only).
- Cite anything not in my library (no hallucinated references possible).
- Make include/exclude decisions without me (it recommends, I decide).
