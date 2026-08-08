from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from core.reminders import find_due_reminders
from storage.tasks_store import TaskStore

NOW = datetime(2026, 8, 8, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def store(tmp_path: Path) -> TaskStore:
    return TaskStore(path=tmp_path / "tasks.json")


def _create_with_deadline(store: TaskStore, hours_from_now: float, **fields) -> dict:
    deadline = (NOW + timedelta(hours=hours_from_now)).isoformat()
    return store.create_task(title="T", task_type="report", deadline=deadline, **fields)


def test_task_20h_out_gets_24h_reminder(store: TaskStore):
    _create_with_deadline(store, 20)
    reminders = find_due_reminders(tasks_store=store, now=NOW)
    assert len(reminders) == 1
    assert reminders[0].threshold_hours == 24


def test_task_3h_out_gets_4h_reminder(store: TaskStore):
    _create_with_deadline(store, 3)
    reminders = find_due_reminders(tasks_store=store, now=NOW)
    assert reminders[0].threshold_hours == 4


def test_task_30min_out_gets_1h_reminder(store: TaskStore):
    _create_with_deadline(store, 0.5)
    reminders = find_due_reminders(tasks_store=store, now=NOW)
    assert reminders[0].threshold_hours == 1


def test_task_30h_out_gets_no_reminder_yet(store: TaskStore):
    _create_with_deadline(store, 30)
    assert find_due_reminders(tasks_store=store, now=NOW) == []


def test_overdue_task_excluded(store: TaskStore):
    _create_with_deadline(store, -2)
    assert find_due_reminders(tasks_store=store, now=NOW) == []


def test_completed_task_excluded_even_if_close(store: TaskStore):
    task = _create_with_deadline(store, 0.5, status="completed")
    assert find_due_reminders(tasks_store=store, now=NOW) == []


def test_task_without_deadline_excluded(store: TaskStore):
    store.create_task(title="No deadline", task_type="report")
    assert find_due_reminders(tasks_store=store, now=NOW) == []
