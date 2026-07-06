# Research Hub

A personal AI-powered literature review workbench for doctoral research on
space autonomy & space robotics. Single user, local-first.

Docs:
- [`docs/IDEAS.md`](docs/IDEAS.md) — concepts and feature ideas
- [`docs/WALKTHROUGH.md`](docs/WALKTHROUGH.md) — the target user experience
- [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md) — build plan and progress tracker (start here)

## Stack

- **Backend**: FastAPI (Python 3.13) — `backend/`
- **Frontend**: Next.js + Tailwind — `frontend/`
- **DB**: SQLite (lives in `data/`, gitignored)
- **LLM**: multi-provider (Claude / OpenAI / Gemini) via LiteLLM, routed per task in `config.yaml`

## Setup

```sh
# 1. Backend
python3 -m venv backend/.venv
backend/.venv/bin/pip install fastapi "uvicorn[standard]" litellm pyyaml python-dotenv pytest httpx

# 2. Frontend
cd frontend && npm install && cd ..

# 3. API keys
cp .env.example .env   # then fill in your keys
```

## Run

```sh
make dev        # backend on :8000 + frontend on :3000
make smoke      # one LLM call per provider (verifies keys)
make test       # backend tests
```

Open http://localhost:3000 — the home page shows backend health and the
LLM task→model routing from `config.yaml`.
