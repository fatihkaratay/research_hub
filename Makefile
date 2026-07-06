BACKEND_PY := backend/.venv/bin/python

.PHONY: dev dev-backend dev-frontend test lint smoke

# Run backend (:8000) and frontend (:3000) together; Ctrl-C stops both.
dev:
	@trap 'kill 0' INT TERM; \
	(cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000) & \
	(cd frontend && npm run dev) & \
	wait

dev-backend:
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && .venv/bin/pytest -q

lint:
	cd frontend && npm run lint

# One LLM call per provider — needs keys in .env
smoke:
	cd backend && .venv/bin/python scripts/smoke_test.py
