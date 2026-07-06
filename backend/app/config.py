"""Load and validate config.yaml (providers + task->model mapping)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config.yaml"

load_dotenv(REPO_ROOT / ".env")


@dataclass(frozen=True)
class TaskConfig:
    model: str  # LiteLLM model string, e.g. "anthropic/claude-opus-4-8"
    max_tokens: int

    @property
    def provider(self) -> str:
        return self.model.split("/", 1)[0]


@dataclass(frozen=True)
class Config:
    providers: dict[str, str]  # provider name -> api_key_env
    tasks: dict[str, TaskConfig]

    def missing_keys(self) -> dict[str, str]:
        """Providers referenced by tasks whose API key env var is unset."""
        used = {t.provider for t in self.tasks.values()}
        return {
            provider: env_var
            for provider, env_var in self.providers.items()
            if provider in used and not os.environ.get(env_var)
        }

    def api_key_for(self, provider: str) -> str:
        env_var = self.providers.get(provider)
        if env_var is None:
            raise ValueError(
                f"Provider '{provider}' is not declared under 'providers' in {CONFIG_PATH}"
            )
        key = os.environ.get(env_var)
        if not key:
            raise RuntimeError(
                f"Environment variable {env_var} (API key for '{provider}') is not set. "
                f"Copy .env.example to .env and fill it in."
            )
        return key


def load_config(path: Path = CONFIG_PATH) -> Config:
    if not path.exists():
        raise FileNotFoundError(f"config.yaml not found at {path}")
    raw = yaml.safe_load(path.read_text())

    providers = {
        name: spec["api_key_env"] for name, spec in (raw.get("providers") or {}).items()
    }
    tasks = {
        name: TaskConfig(model=spec["model"], max_tokens=int(spec.get("max_tokens", 4096)))
        for name, spec in (raw.get("tasks") or {}).items()
    }
    if not tasks:
        raise ValueError(f"No tasks defined in {path}")

    for name, task in tasks.items():
        if task.provider not in providers:
            raise ValueError(
                f"Task '{name}' uses provider '{task.provider}' which is not declared "
                f"under 'providers' in {path}"
            )
    return Config(providers=providers, tasks=tasks)


config = load_config()
