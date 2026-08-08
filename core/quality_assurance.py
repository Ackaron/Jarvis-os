"""Quality Assurance checklist builder (SPECIFICATION.md -> Learning System ->
Quality Assurance). Reads stakeholder.metadata.usual_checks (built over time
from corrections); falls back to a generic checklist for new/unknown
stakeholders.
"""

from __future__ import annotations

from typing import Optional

GENERIC_CHECKLIST = ["Данные проверены", "Форматирование корректно"]


def build_checklist(stakeholder: Optional[dict]) -> list[str]:
    if not stakeholder:
        return list(GENERIC_CHECKLIST)
    checks = (stakeholder.get("metadata") or {}).get("usual_checks")
    if not checks:
        return list(GENERIC_CHECKLIST)
    return list(checks)


def format_qa_prompt(stakeholder: Optional[dict]) -> str:
    checklist = build_checklist(stakeholder)
    lines = "\n".join(f"☐ {item}" for item in checklist)
    return f"Перед завершением проверь:\n{lines}"
