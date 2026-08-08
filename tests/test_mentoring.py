from pathlib import Path

import pytest

from core.mentoring import explain_task
from storage.decisions_store import DecisionStore


@pytest.fixture
def store(tmp_path: Path) -> DecisionStore:
    return DecisionStore(path=tmp_path / "decisions.json")


def test_no_decisions_gives_default_explanation(store: DecisionStore):
    explanation = explain_task("task-1", decisions_store=store)
    assert "не было" in explanation


def test_explanation_includes_reasoning(store: DecisionStore):
    store.log_decision(
        task_id="task-1",
        decision_type="content",
        field_changed="slide_3",
        reasoning="Трутнев не интересуется партнёрами",
    )
    explanation = explain_task("task-1", decisions_store=store)
    assert "Трутнев не интересуется партнёрами" in explanation
    assert "slide_3" in explanation


def test_explanation_includes_stakeholder_focus(store: DecisionStore):
    store.log_decision(task_id="task-1", decision_type="content", reasoning="reason")
    stakeholder = {"name": "Трутнев", "metadata": {"focus_areas": ["Инвестиции", "Продукты"]}}
    explanation = explain_task("task-1", stakeholder=stakeholder, decisions_store=store)
    assert "Инвестиции" in explanation
