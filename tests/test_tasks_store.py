from pathlib import Path

import pytest

from storage.tasks_store import TaskNotFoundError, TaskStore


@pytest.fixture
def store(tmp_path: Path) -> TaskStore:
    return TaskStore(path=tmp_path / "tasks.json")


def test_create_task_assigns_id_and_defaults(store: TaskStore):
    task = store.create_task(title="Презентация резидентов", task_type="presentation")
    assert task["id"]
    assert task["status"] == "queued"
    assert task["created_at"] == task["updated_at"]


def test_get_task_roundtrip(store: TaskStore):
    created = store.create_task(title="Отчет по бару", task_type="report")
    fetched = store.get_task(created["id"])
    assert fetched == created


def test_get_missing_task_raises(store: TaskStore):
    with pytest.raises(TaskNotFoundError):
        store.get_task("does-not-exist")


def test_list_tasks_filters_by_status(store: TaskStore):
    a = store.create_task(title="A", task_type="email")
    b = store.create_task(title="B", task_type="report")
    store.update_task(b["id"], status="completed")

    queued = store.list_tasks(status="queued")
    completed = store.list_tasks(status="completed")

    assert [t["id"] for t in queued] == [a["id"]]
    assert [t["id"] for t in completed] == [b["id"]]


def test_update_task_changes_updated_at(store: TaskStore):
    task = store.create_task(title="C", task_type="email")
    updated = store.update_task(task["id"], status="in_progress")
    assert updated["status"] == "in_progress"
    assert updated["updated_at"] >= task["updated_at"]


def test_update_missing_task_raises(store: TaskStore):
    with pytest.raises(TaskNotFoundError):
        store.update_task("does-not-exist", status="completed")


def test_store_persists_across_instances(tmp_path: Path):
    path = tmp_path / "tasks.json"
    store_a = TaskStore(path=path)
    task = store_a.create_task(title="Persisted", task_type="email")

    store_b = TaskStore(path=path)
    assert store_b.get_task(task["id"])["title"] == "Persisted"
