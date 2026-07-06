"""Single entry point for all LLM calls, routed by task name via LiteLLM."""

from __future__ import annotations

import litellm

from app.config import config

Message = dict[str, str]  # {"role": ..., "content": ...}


def complete(task: str, messages: list[Message], **overrides) -> str:
    """Run the configured model for `task` on `messages`, return the text."""
    task_cfg = config.tasks.get(task)
    if task_cfg is None:
        raise ValueError(
            f"Unknown task '{task}'. Configured tasks: {sorted(config.tasks)}"
        )

    response = litellm.completion(
        model=task_cfg.model,
        messages=messages,
        max_tokens=overrides.pop("max_tokens", task_cfg.max_tokens),
        api_key=config.api_key_for(task_cfg.provider),
        **overrides,
    )
    return response.choices[0].message.content
