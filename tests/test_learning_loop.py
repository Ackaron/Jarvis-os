import json
from pathlib import Path

import pytest

from core.learning_loop import derive_profile_updates
from storage.decisions_store import DecisionStore


@pytest.fixture
def store(tmp_path: Path) -> DecisionStore:
    return DecisionStore(path=tmp_path / "decisions.json")


def test_no_decisions_returns_empty_dict(store: DecisionStore):
    assert derive_profile_updates("Трутнев", decisions_store=store) == {}


def test_extracts_focus_and_anti_focus_from_llm_json(store: DecisionStore):
    store.log_decision(
        task_id="t1", decision_type="content", reasoning="Не интересуется партнёрами"
    )

    def fake_caller(model_name, task):
        return {
            "text": json.dumps({"focus_areas": ["Инвестиции"], "anti_focus": ["Партнёры"]})
        }

    updates = derive_profile_updates("Трутнев", decisions_store=store, llm_caller=fake_caller)
    assert updates == {"focus_areas": ["Инвестиции"], "anti_focus": ["Партнёры"]}


def test_malformed_llm_response_returns_empty_dict(store: DecisionStore):
    store.log_decision(task_id="t1", decision_type="content", reasoning="reason")

    def broken_caller(model_name, task):
        return {"text": "not valid json"}

    assert derive_profile_updates("Трутнев", decisions_store=store, llm_caller=broken_caller) == {}


def test_scopes_to_task_id_when_given(store: DecisionStore):
    store.log_decision(task_id="t1", decision_type="content", reasoning="reason for t1")
    store.log_decision(task_id="t2", decision_type="content", reasoning="reason for t2")

    seen_prompts = []

    def capturing_caller(model_name, task):
        seen_prompts.append(task["prompt"])
        return {"text": json.dumps({"focus_areas": [], "anti_focus": []})}

    derive_profile_updates(
        "Трутнев", task_id="t1", decisions_store=store, llm_caller=capturing_caller
    )
    assert "reason for t1" in seen_prompts[0]
    assert "reason for t2" not in seen_prompts[0]
