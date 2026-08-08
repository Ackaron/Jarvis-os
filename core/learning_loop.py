"""Learning Loop: turns free-text correction reasoning into structured
stakeholder profile updates (SPECIFICATION.md -> Stakeholder Profiling).
Uses the same LLM-via-DI pattern as workflows (see ADR-005/ADR-006) — no real
API key is required to build or test this.
"""

from __future__ import annotations

import json
from typing import Callable, Optional

from core.llm_dispatch import call_model
from core.llm_router import execute_with_fallback, route_task
from storage.decisions_store import DecisionStore

LLMCaller = Callable[[str, dict], dict]

EXTRACTION_SYSTEM_PROMPT = (
    "Ты извлекаешь структурированные предпочтения стейкхолдера из истории правок. "
    'Отвечай ТОЛЬКО валидным JSON вида {"focus_areas": [...], "anti_focus": [...]}. '
    "Никакого текста вокруг."
)


def derive_profile_updates(
    stakeholder_name: str,
    task_id: Optional[str] = None,
    decisions_store: Optional[DecisionStore] = None,
    llm_caller: LLMCaller = call_model,
) -> dict:
    """Reads decisions (optionally scoped to one task) and asks the LLM to
    extract focus_areas/anti_focus deltas. Returns {} if there's nothing to
    learn from, or if the LLM's response wasn't parseable JSON."""
    decisions_store = decisions_store or DecisionStore()
    decisions = decisions_store.list_decisions(task_id=task_id)

    reasoning_lines = "\n".join(f"- {d['reasoning']}" for d in decisions if d.get("reasoning"))
    if not reasoning_lines:
        return {}

    decision = route_task("task_classification")
    result = execute_with_fallback(
        decision,
        {
            "prompt": (
                f"Стейкхолдер: {stakeholder_name}\n\nПричины правок:\n{reasoning_lines}\n\n"
                "Извлеки focus_areas (на чём фокусироваться) и anti_focus (чего избегать)."
            ),
            "system": EXTRACTION_SYSTEM_PROMPT,
        },
        caller=llm_caller,
    )

    try:
        parsed = json.loads(result["text"])
    except (json.JSONDecodeError, TypeError):
        return {}

    updates = {}
    if isinstance(parsed.get("focus_areas"), list):
        updates["focus_areas"] = parsed["focus_areas"]
    if isinstance(parsed.get("anti_focus"), list):
        updates["anti_focus"] = parsed["anti_focus"]
    return updates
