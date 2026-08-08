"""Local JSON-backed task storage for Phase 0 (no Supabase/Postgres yet, see ADR-004).

Field names loosely follow the `tasks` table in SPECIFICATION.md, simplified
for a single local JSON file instead of a Postgres schema with RLS.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_STORE_PATH = Path(__file__).resolve().parent / "tasks.json"


class TaskNotFoundError(KeyError):
    """Raised when a task_id does not exist in the store."""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskStore:
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

    def _write_all(self, tasks: list[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)

    def create_task(self, title: str, task_type: str, **fields) -> dict:
        tasks = self._read_all()
        now = _now_iso()
        task = {
            "id": str(uuid.uuid4()),
            "title": title,
            "task_type": task_type,
            "status": "queued",
            "created_at": now,
            "updated_at": now,
            **fields,
        }
        tasks.append(task)
        self._write_all(tasks)
        return task

    def get_task(self, task_id: str) -> dict:
        for task in self._read_all():
            if task["id"] == task_id:
                return task
        raise TaskNotFoundError(task_id)

    def list_tasks(self, status: Optional[str] = None) -> list[dict]:
        tasks = self._read_all()
        if status is None:
            return tasks
        return [t for t in tasks if t.get("status") == status]

    def update_task(self, task_id: str, **fields) -> dict:
        tasks = self._read_all()
        for task in tasks:
            if task["id"] == task_id:
                task.update(fields)
                task["updated_at"] = _now_iso()
                self._write_all(tasks)
                return task
        raise TaskNotFoundError(task_id)
