from pathlib import Path

import pytest

from storage.decisions_store import DecisionStore
from storage.tasks_store import TaskStore
from tests.helpers import ScriptedHumanInput
from workflows.engine import Workflow


class _EchoWorkflow(Workflow):
    steps = ["say_hello", "ask_name"]

    def say_hello(self) -> str:
        return "hello"

    def ask_name(self) -> str:
        return self.ask("What's your name?")


@pytest.fixture
def stores(tmp_path: Path) -> tuple[TaskStore, DecisionStore]:
    tasks = TaskStore(path=tmp_path / "tasks.json")
    decisions = DecisionStore(path=tmp_path / "decisions.json")
    return tasks, decisions


def test_run_executes_steps_in_order_and_updates_task_status(stores):
    tasks_store, decisions_store = stores
    task = tasks_store.create_task(title="Test", task_type="other")

    workflow = _EchoWorkflow(
        task["id"],
        human_input=ScriptedHumanInput(["Viktor"]),
        tasks_store=tasks_store,
        decisions_store=decisions_store,
    )
    state = workflow.run()

    assert state == {"say_hello": "hello", "ask_name": "Viktor"}
    assert tasks_store.get_task(task["id"])["status"] == "awaiting_review"


def test_complete_sets_status_and_iterations_count(stores):
    tasks_store, decisions_store = stores
    task = tasks_store.create_task(title="Test", task_type="other")
    workflow = _EchoWorkflow(
        task["id"],
        human_input=ScriptedHumanInput(["Viktor"]),
        tasks_store=tasks_store,
        decisions_store=decisions_store,
    )
    workflow.run()
    workflow.record_correction("content", "ask_name", "Viktor", "Victor", "spelling")
    result = workflow.complete()

    assert result == workflow.state
    completed = tasks_store.get_task(task["id"])
    assert completed["status"] == "completed"
    assert completed["iterations_count"] == 1


def test_explain_reports_no_corrections_by_default(stores):
    tasks_store, decisions_store = stores
    task = tasks_store.create_task(title="Test", task_type="other")
    workflow = _EchoWorkflow(
        task["id"],
        human_input=ScriptedHumanInput(["Viktor"]),
        tasks_store=tasks_store,
        decisions_store=decisions_store,
    )
    workflow.run()
    assert "не было" in workflow.explain()
