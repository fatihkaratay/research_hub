"""Prove each configured provider answers a trivial prompt.

Usage:  cd backend && .venv/bin/python scripts/smoke_test.py
Needs the provider API keys set in ../.env (see .env.example).
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# app must be imported before litellm: app/__init__.py sets SSL_CERT_FILE,
# which litellm's HTTP stack reads at import time.
from app.config import config  # noqa: E402

import litellm  # noqa: E402

# One cheap model per provider, just to prove the key + wiring work.
PROBE_MODELS = {
    "anthropic": "anthropic/claude-haiku-4-5",
    "openai": "openai/gpt-5-mini",
    "gemini": "gemini/gemini-2.5-flash",
}


def main() -> int:
    failures = 0
    used_providers = sorted({t.provider for t in config.tasks.values()} | set(PROBE_MODELS))
    for provider in used_providers:
        model = PROBE_MODELS.get(provider)
        if model is None:
            print(f"  {provider}: no probe model defined, skipping")
            continue
        env_var = config.providers.get(provider)
        if env_var and not os.environ.get(env_var):
            print(f"  {provider}: skipped — {env_var} not set in .env")
            continue
        try:
            api_key = config.api_key_for(provider)
            response = litellm.completion(
                model=model,
                messages=[{"role": "user", "content": "Say hi in exactly two words."}],
                max_tokens=100,
                api_key=api_key,
            )
            text = (response.choices[0].message.content or "").strip()
            print(f"  {provider} ({model}): OK — {text!r}")
        except Exception as exc:  # noqa: BLE001 — report and continue to next provider
            failures += 1
            print(f"  {provider} ({model}): FAILED — {exc}")
    return 1 if failures else 0


if __name__ == "__main__":
    print("LLM smoke test — one call per provider:")
    raise SystemExit(main())
