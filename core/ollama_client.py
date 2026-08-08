"""Real Ollama API client — local, no key needed (see ADR-007: promoted to
primary while Anthropic/Claude access via omniroute is unresolved). Talks to
Ollama's local REST API (POST /api/chat). The HTTP client is injectable so
this is testable without a running Ollama instance.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import core.env  # noqa: F401  side effect: loads .env
from core.config_loader import get_routing_config

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"


class UnsupportedModelProviderError(ValueError):
    """Raised when asked to call a model this client doesn't know how to reach."""


def _get_http_client() -> Any:
    import httpx  # lazy import: only required for real calls

    base_url = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)
    return httpx.Client(base_url=base_url, timeout=120.0)


def call_ollama(
    model_name: str,
    task: dict,
    config: Optional[dict] = None,
    client: Optional[Any] = None,
) -> dict:
    """`task` must contain 'prompt' (str) and may contain 'system' (str).
    `client` lets tests inject a fake HTTP client (httpx.Client-shaped:
    `.post(path, json=...)` returning something with `.raise_for_status()`
    and `.json()`)."""
    config = config if config is not None else get_routing_config()
    model_info = (config.get("models") or {}).get(model_name)
    if model_info is None or model_info.get("api_provider") != "local":
        raise UnsupportedModelProviderError(
            f"'{model_name}' is not a local/Ollama model in routing.yaml (or is "
            "missing); this caller only handles api_provider: local."
        )

    prompt = task.get("prompt")
    if not prompt:
        raise ValueError("task['prompt'] is required to call an LLM model")

    api_model_id = model_info.get("api_model_id", model_name)
    owns_client = client is None
    client = client if client is not None else _get_http_client()

    messages = []
    system = task.get("system")
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.post(
            "/api/chat",
            json={"model": api_model_id, "messages": messages, "stream": False},
        )
        response.raise_for_status()
        data = response.json()
    finally:
        if owns_client:
            client.close()

    return {"model_used": api_model_id, "text": data["message"]["content"]}
