"""Unified LLM caller (see ADR-007): dispatches to the right provider-
specific client based on `api_provider` in vault/system/routing.yaml.

Workflows and interfaces import `call_model` from here instead of a specific
provider's client (core.llm_client.call_anthropic, core.ollama_client.call_ollama)
so switching the active provider is a routing.yaml edit, not a code change —
this is exactly how Viktor moved primary routing from Anthropic to Ollama
without touching workflows/engine.py or any of the three workflows.
"""

from __future__ import annotations

from typing import Optional

from core.config_loader import get_routing_config
from core.llm_client import call_anthropic
from core.ollama_client import call_ollama

PROVIDER_CALLERS = {
    "anthropic": call_anthropic,
    "local": call_ollama,
}


class UnknownProviderError(ValueError):
    """Raised when a model is undefined, or its api_provider has no caller."""


def call_model(model_name: str, task: dict, config: Optional[dict] = None) -> dict:
    config = config if config is not None else get_routing_config()
    model_info = (config.get("models") or {}).get(model_name)
    if model_info is None:
        raise UnknownProviderError(f"'{model_name}' is not defined in routing.yaml models.")

    provider = model_info.get("api_provider")
    caller = PROVIDER_CALLERS.get(provider)
    if caller is None:
        raise UnknownProviderError(f"No caller registered for api_provider '{provider}'.")

    return caller(model_name, task, config=config)
