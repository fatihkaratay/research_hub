import logging

from fastapi import FastAPI

from app.config import config

logger = logging.getLogger("research_hub")

app = FastAPI(title="Research Hub API")


@app.on_event("startup")
def check_api_keys() -> None:
    # Warn (don't crash) so the app is usable without keys; the LLM adapter
    # raises a clear error if a keyless provider is actually invoked.
    missing = config.missing_keys()
    for provider, env_var in missing.items():
        logger.warning(
            "API key for provider '%s' is not set (%s) — LLM tasks using it will fail. "
            "Copy .env.example to .env and fill it in.",
            provider,
            env_var,
        )


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "tasks": {name: t.model for name, t in config.tasks.items()},
        "missing_api_keys": list(config.missing_keys().values()),
    }
