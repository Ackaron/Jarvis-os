"""Classifies an incoming task description into type/domain/urgency/autonomy.

Rule-based per Phase 0 scope (no LLM call yet, see JARVIS_OS_ARCHITECTURE.md -> Intent Router
and ADR-004). Domain matching reads vault/system/domains.yaml via core.config_loader.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from core.config_loader import get_domains_config

TASK_TYPE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "presentation": ("презентац", "слайд", "pptx", "presentation", "slide"),
    "email": ("письмо", "email", "почт", "e-mail"),
    "research": ("исследован", "анализ рынка", "market research", "research"),
    "report": ("отчет", "отчёт", "report"),
    "analysis": ("анализ", "analysis", "проанализ"),
    "automation": ("автоматизац", "automation", "workflow", "n8n"),
}

# Order matters: more specific categories (e.g. "research") must be checked
# before more generic ones (e.g. "analysis") since "анализ рынка" contains "анализ".
TASK_TYPE_PRIORITY = ("presentation", "email", "research", "report", "analysis", "automation")

URGENCY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "critical": ("критично", "критическ", "critical", "срочно как можно быстрее"),
    "priority": ("срочно", "приоритет", "важно", "priority", "urgent"),
}

# Whether Jarvis can attempt this task type without asking Viktor first.
# Matches the intent behind JARVIS_OS_ARCHITECTURE.md's Intent Router pseudocode.
DEFAULT_AUTONOMY: dict[str, bool] = {
    "presentation": False,
    "email": True,
    "research": False,
    "report": True,
    "analysis": False,
    "automation": True,
    "other": False,
}


@dataclass
class IntentResult:
    task_type: str
    domain: Optional[str] = None
    urgency: str = "routine"
    stakeholder: Optional[str] = None
    autonomous: bool = False
    matched_keywords: list[str] = field(default_factory=list)


def _match_task_type(text_lower: str) -> tuple[str, list[str]]:
    for task_type in TASK_TYPE_PRIORITY:
        keywords = TASK_TYPE_KEYWORDS[task_type]
        matched = [kw for kw in keywords if kw in text_lower]
        if matched:
            return task_type, matched
    return "other", []


def _match_domain(text_lower: str, domains_config: dict) -> Optional[str]:
    for domain_id, domain in (domains_config.get("domains") or {}).items():
        candidates = [domain.get("name", "")] + list(domain.get("aliases", []))
        for candidate in candidates:
            if candidate and candidate.lower() in text_lower:
                return domain_id
    return None


def _match_urgency(text_lower: str) -> str:
    for level in ("critical", "priority"):
        if any(kw in text_lower for kw in URGENCY_KEYWORDS[level]):
            return level
    return "routine"


def _match_stakeholder(text_lower: str, known_stakeholders: Optional[list[str]]) -> Optional[str]:
    if not known_stakeholders:
        return None
    for name in known_stakeholders:
        if name.lower() in text_lower:
            return name
    return None


def classify_intent(
    text: str,
    domains_config: Optional[dict] = None,
    known_stakeholders: Optional[list[str]] = None,
) -> IntentResult:
    """Classifies free-text task input. Pass domains_config explicitly in tests
    to avoid depending on the real vault/system/domains.yaml on disk."""
    if domains_config is None:
        domains_config = get_domains_config()

    text_lower = text.lower()
    task_type, matched_keywords = _match_task_type(text_lower)

    return IntentResult(
        task_type=task_type,
        domain=_match_domain(text_lower, domains_config),
        urgency=_match_urgency(text_lower),
        stakeholder=_match_stakeholder(text_lower, known_stakeholders),
        autonomous=DEFAULT_AUTONOMY.get(task_type, False),
        matched_keywords=matched_keywords,
    )
