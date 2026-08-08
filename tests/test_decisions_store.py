from pathlib import Path

import pytest

from storage.decisions_store import DecisionStore


@pytest.fixture
def store(tmp_path: Path) -> DecisionStore:
    return DecisionStore(path=tmp_path / "decisions.json")


def test_log_decision_assigns_id_and_timestamp(store: DecisionStore):
    decision = store.log_decision(
        task_id="task-1",
        decision_type="content",
        reasoning="Трутнев не интересуется партнёрами",
        field_changed="slide_3",
        original_value="Партнёры",
        new_value="Инвестиции",
    )
    assert decision["id"]
    assert decision["created_at"]
    assert decision["task_id"] == "task-1"


def test_list_decisions_filters_by_task_id(store: DecisionStore):
    store.log_decision(task_id="task-1", decision_type="content", reasoning="a")
    store.log_decision(task_id="task-2", decision_type="tone", reasoning="b")

    task_1_decisions = store.list_decisions(task_id="task-1")
    assert len(task_1_decisions) == 1
    assert task_1_decisions[0]["reasoning"] == "a"


def test_list_decisions_without_filter_returns_all(store: DecisionStore):
    store.log_decision(task_id="task-1", decision_type="content", reasoning="a")
    store.log_decision(task_id="task-2", decision_type="tone", reasoning="b")
    assert len(store.list_decisions()) == 2


def test_metadata_kwargs_are_captured(store: DecisionStore):
    decision = store.log_decision(
        task_id="task-1", decision_type="content", reasoning="a", workflow="email"
    )
    assert decision["metadata"] == {"workflow": "email"}
