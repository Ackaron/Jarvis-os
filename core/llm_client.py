"""Real Anthropic API client — the default `caller` workflows pass to
`core.llm_router.execute_with_fallback` (see ADR-005).

Only handles models with `api_provider: anthropic` in vault/system/routing.yaml.
Ollama/local models need a different caller (Phase 2+). The Anthropic client
itself is injectable so callers can be tested without a real API key.
"""

from __future__ import annotations

import os
from typing import Any, Optional

from core.config_loader import get_routing_config


class AnthropicNotConfiguredError(RuntimeError):
    """Raised when ANTHROPIC_API_KEY is missing and no client was injected."""


class UnsupportedModelProviderError(ValueError):
    """Raised when asked to call a model this client doesn't know how to reach."""


def _get_anthropic_client() -> Any:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise AnthropicNotConfiguredError(
            "ANTHROPIC_API_KEY is not set (see .env.example). Real LLM calls need "
            "it; workflow logic can still be tested via an injected fake caller/client."
        )
    from anthropic import Anthropic  # lazy import: only required for real calls

    return Anthropic(api_key=api_key)


def call_anthropic(
    model_name: str,
    task: dict,
    config: Optional[dict] = None,
    client: Optional[Any] = None,
) -> dict:
    """`task` must contain 'prompt' (str) and may contain 'system' (str) and
    'max_tokens' (int). `client` lets tests inject a fake Anthropic client."""
    config = config if config is not None else get_routing_config()
    model_info = (config.get("models") or {}).get(model_name)
    if model_info is None or model_info.get("api_provider") != "anthropic":
        raise UnsupportedModelProviderError(
            f"'{model_name}' is not an Anthropic model in routing.yaml (or is "
            "missing); this caller only handles api_provider: anthropic."
        )

    prompt = task.get("prompt")
    if not prompt:
        raise ValueError("task['prompt'] is required to call an LLM model")

    api_model_id = model_info.get("api_model_id", model_name)
    client = client if client is not None else _get_anthropic_client()

    response = client.messages.create(
        model=api_model_id,
        max_tokens=task.get("max_tokens", 1024),
        system=task.get("system", ""),
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )
    return {"model_used": api_model_id, "text": text}
