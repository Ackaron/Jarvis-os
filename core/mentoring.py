"""Mentoring Mode: explains past decisions on request (SPECIFICATION.md ->
Learning System -> Mentoring Mode). Assembles the explanation from stored
decisions + stakeholder profile — no LLM call needed for this to be useful.
"""

from __future__ import annotations

from typing import Optional

from storage.decisions_store import DecisionStore


def explain_task(
    task_id: str,
    stakeholder: Optional[dict] = None,
    decisions_store: Optional[DecisionStore] = None,
) -> str:
    decisions_store = decisions_store or DecisionStore()
    decisions = decisions_store.list_decisions(task_id=task_id)

    if not decisions:
        explanation = "Правок по этой задаче не было — всё прошло по стандартному плану."
    else:
        lines = [
            f"Правка ({d['decision_type']}, поле '{d.get('field_changed', '?')}'): {d['reasoning']}"
            for d in decisions
        ]
        explanation = "\n".join(lines)

    if stakeholder:
        focus = (stakeholder.get("metadata") or {}).get("focus_areas")
        if focus:
            explanation += (
                f"\n\nКонтекст: {stakeholder['name']} обычно фокусируется на: "
                f"{', '.join(focus)}."
            )

    return explanation
