"""Local JSON-backed decisions log — питает Why Extraction (see ADR-005).

Mirrors the `decisions` table shape from SPECIFICATION.md, simplified for a
single local JSON file (no Postgres on Phase 0/1, see ADR-004).
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_STORE_PATH = Path(__file__).resolve().parent / "decisions.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DecisionStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else DEFAULT_STORE_PATH
        if not self.path.exists():
            self._write_all([])

    def _read_all(self) -> list[dict]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else []

    def _write_all(self, decisions: list[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(decisions, f, ensure_ascii=False, indent=2)

    def log_decision(
        self,
        task_id: str,
        decision_type: str,
        reasoning: str,
        field_changed: Optional[str] = None,
        original_value: Optional[str] = None,
        new_value: Optional[str] = None,
        **metadata,
    ) -> dict:
        decisions = self._read_all()
        decision = {
            "id": str(uuid.uuid4()),
            "task_id": task_id,
            "decision_type": decision_type,
            "field_changed": field_changed,
            "original_value": original_value,
            "new_value": new_value,
            "reasoning": reasoning,
            "created_at": _now_iso(),
            "metadata": metadata,
        }
        decisions.append(decision)
        self._write_all(decisions)
        return decision

    def list_decisions(self, task_id: Optional[str] = None) -> list[dict]:
        decisions = self._read_all()
        if task_id is None:
            return decisions
        return [d for d in decisions if d.get("task_id") == task_id]
