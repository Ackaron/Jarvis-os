from pathlib import Path

import pytest

from core.estimation import DEFAULT_ESTIMATE_SECONDS, estimate_duration
from storage.tasks_store import TaskStore


@pytest.fixture
def store(tmp_path: Path) -> TaskStore:
    return TaskStore(path=tmp_path / "tasks.json")


def test_no_history_returns_default(store: TaskStore):
    estimate = estimate_duration("presentation", tasks_store=store)
    assert estimate.estimated_seconds == DEFAULT_ESTIMATE_SECONDS
    assert estimate.sample_size == 0
    assert estimate.confidence < 0.5


def test_uses_average_of_completed_tasks_of_same_type(store: TaskStore):
    for seconds in (1800, 2000, 2200):
        task = store.create_task(title="P", task_type="presentation")
        store.update_task(task["id"], status="completed", time_actual_seconds=seconds)

    estimate = estimate_duration("presentation", tasks_store=store)
    assert estimate.estimated_seconds == 2000
    assert estimate.sample_size == 3


def test_ignores_other_task_types_and_incomplete_tasks(store: TaskStore):
    presentation = store.create_task(title="P", task_type="presentation")
    store.update_task(presentation["id"], status="completed", time_actual_seconds=3000)

    email = store.create_task(title="E", task_type="email")
    store.update_task(email["id"], status="completed", time_actual_seconds=100)

    still_queued = store.create_task(title="P2", task_type="presentation")
    # no time_actual_seconds set, not completed

    estimate = estimate_duration("presentation", tasks_store=store)
    assert estimate.sample_size == 1
    assert estimate.estimated_seconds == 3000


def test_low_sample_size_has_moderate_confidence(store: TaskStore):
    task = store.create_task(title="P", task_type="presentation")
    store.update_task(task["id"], status="completed", time_actual_seconds=1500)
    estimate = estimate_duration("presentation", tasks_store=store)
    assert estimate.confidence == 0.5
