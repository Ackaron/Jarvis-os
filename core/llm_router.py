"""Resolves which LLM should handle a task, per vault/system/routing.yaml.

Phase 0 scope (ADR-004): this module only decides *which* model to use and in
what fallback order. It does not call any real LLM API yet — `call_model` is a
stub that Phase 1 will replace with a real Anthropic/Ollama client.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from core.config_loader import get_routing_config


class AllModelsFailedError(RuntimeError):
    """Raised when every model in a routing decision's chain has failed."""


@dataclass
class RoutingDecision:
    task_type: str
    primary_model: str
    fallback_chain: list[str] = field(default_factory=list)
    fallback_allowed: bool = True
    observer: Optional[str] = None
    reason: Optional[str] = None

    @property
    def chain(self) -> list[str]:
        """Full ordered attempt list: primary first, then fallbacks (if allowed)."""
        if not self.fallback_allowed:
            return [self.primary_model]
        return [self.primary_model, *self.fallback_chain]


def route_task(task_type: str, config: Optional[dict] = None) -> RoutingDecision:
    config = config if config is not None else get_routing_config()
    defaults = config.get("defaults", {})
    rule = (config.get("routing_rules") or {}).get(task_type)

    if rule is None:
        return RoutingDecision(
            task_type=task_type,
            primary_model=defaults.get("primary_model", "claude-sonnet"),
            fallback_chain=list(defaults.get("fallback_chain", [])),
            fallback_allowed=True,
            reason="no specific routing_rules entry; using defaults",
        )

    raw_fallback = rule.get("fallback", defaults.get("fallback_chain", []))
    if raw_fallback is False:
        fallback_chain: list[str] = []
        fallback_allowed = False
    else:
        fallback_chain = list(raw_fallback) if raw_fallback else []
        fallback_allowed = True

    return RoutingDecision(
        task_type=task_type,
        primary_model=rule.get("primary", defaults.get("primary_model", "claude-sonnet")),
        fallback_chain=fallback_chain,
        fallback_allowed=fallback_allowed,
        observer=rule.get("observer"),
        reason=rule.get("reason"),
    )


def call_model(model_name: str, task: dict) -> dict:
    """Stub — Phase 0 has no real LLM client wired up (see ADR-004)."""
    raise NotImplementedError(
        f"Model '{model_name}' cannot be called yet: LLM integration is Phase 1+. "
        "This stub exists so routing logic can be tested without live API calls."
    )


def execute_with_fallback(
    decision: RoutingDecision,
    task: dict,
    caller: Callable[[str, dict], dict] = call_model,
) -> dict:
    """Tries each model in decision.chain in order; raises AllModelsFailedError
    if every attempt fails. Mirrors the fallback pseudocode in SPECIFICATION.md."""
    last_error: Optional[Exception] = None
    for model_name in decision.chain:
        try:
            return caller(model_name, task)
        except Exception as exc:  # noqa: BLE001 - intentionally broad, mirrors spec fallback loop
            last_error = exc
            continue
    raise AllModelsFailedError(
        f"All models failed for task_type '{decision.task_type}': {decision.chain}"
    ) from last_error
