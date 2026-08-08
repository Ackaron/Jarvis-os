from pathlib import Path

import pytest

from storage.decisions_store import DecisionStore
from storage.tasks_store import TaskStore
from tests.helpers import ScriptedHumanInput, fake_llm_caller
from workflows.email_workflow import EmailWorkflow


@pytest.fixture
def stores(tmp_path: Path):
    return (
        TaskStore(path=tmp_path / "tasks.json"),
        DecisionStore(path=tmp_path / "decisions.json"),
    )


def test_email_workflow_without_corrections(stores):
    tasks_store, decisions_store = stores
    task = tasks_store.create_task(title="Email to УК", task_type="email")

    human_input = ScriptedHumanInput(
        [
            "Письмо от УК про статус резидента",  # intake_letter
            "Подтвердить контракт активен, платежи по графику",  # collect_thesis
            "",  # review_response: no corrections
        ]
    )
    workflow = EmailWorkflow(
        task["id"],
        human_input=human_input,
        llm_caller=fake_llm_caller,
        tasks_store=tasks_store,
        decisions_store=decisions_store,
    )
    state = workflow.run()

    assert "[claude-sonnet]" in state["analyze_content"] or "[claude-opus]" in state["analyze_content"]
    assert state["review_response"] == state["generate_response"]
    assert decisions_store.list_decisions(task_id=task["id"]) == []


def test_email_workflow_with_correction_logs_decision_and_regenerates(stores):
    tasks_store, decisions_store = stores
    task = tasks_store.create_task(title="Email to Фонд", task_type="email")

    human_input = ScriptedHumanInput(
        [
            "Письмо от Фонда",  # intake_letter
            "Подтвердить льготу Q4",  # collect_thesis
            "Добавь подробнее про льготу Q4",  # review_response feedback
            "Виктор попросил детализировать условия льготы",  # reasoning
        ]
    )
    workflow = EmailWorkflow(
        task["id"],
        human_input=human_input,
        llm_caller=fake_llm_caller,
        tasks_store=tasks_store,
        decisions_store=decisions_store,
    )
    workflow.run()

    decisions = decisions_store.list_decisions(task_id=task["id"])
    assert len(decisions) == 1
    assert decisions[0]["reasoning"] == "Виктор попросил детализировать условия льготы"
    assert workflow.state["review_response"] != workflow.state["generate_response"]
