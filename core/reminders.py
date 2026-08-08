"""Reminder logic (SPECIFICATION.md -> Task Management -> reminders): which
tasks need a reminder at 24h/4h/1h before their deadline. Delivery channel is
injected by the caller — see interfaces/telegram_bot.py or ADR-006.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from storage.tasks_store import TaskStore

REMINDER_THRESHOLDS_HOURS: tuple[int, ...] = (1, 4, 24)
TERMINAL_STATUSES = ("completed", "failed")


@dataclass
class Reminder:
    task_id: str
    title: str
    hours_until_deadline: float
    threshold_hours: int


def find_due_reminders(
    tasks_store: Optional[TaskStore] = None,
    now: Optional[datetime] = None,
    thresholds_hours: tuple[int, ...] = REMINDER_THRESHOLDS_HOURS,
) -> list[Reminder]:
    tasks_store = tasks_store or TaskStore()
    now = now or datetime.now(timezone.utc)
    ascending_thresholds = sorted(thresholds_hours)

    reminders: list[Reminder] = []
    for task in tasks_store.list_tasks():
        deadline_str = task.get("deadline")
        if not deadline_str or task.get("status") in TERMINAL_STATUSES:
            continue

        deadline = datetime.fromisoformat(deadline_str)
        hours_left = (deadline - now).total_seconds() / 3600
        if hours_left <= 0:
            continue

        for threshold in ascending_thresholds:
            if hours_left <= threshold:
                reminders.append(
                    Reminder(
                        task_id=task["id"],
                        title=task["title"],
                        hours_until_deadline=round(hours_left, 1),
                        threshold_hours=threshold,
                    )
                )
                break

    return reminders
