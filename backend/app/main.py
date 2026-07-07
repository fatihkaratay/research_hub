import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import config
from app.routers import papers, projects

logger = logging.getLogger("research_hub")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warn (don't crash) so the app is usable without keys; the LLM adapter
    # raises a clear error if a keyless provider is actually invoked.
    for provider, env_var in config.missing_keys().items():
        logger.warning(
            "API key for provider '%s' is not set (%s) — LLM tasks using it will fail. "
            "Copy .env.example to .env and fill it in.",
            provider,
            env_var,
        )
    yield


app = FastAPI(title="Research Hub API", lifespan=lifespan)
app.include_router(projects.router)
app.include_router(papers.router)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "tasks": {name: t.model for name, t in config.tasks.items()},
        "missing_api_keys": list(config.missing_keys().values()),
    }
