from pathlib import Path

import pytest

from core.system_prompt import BASE_SYSTEM_PROMPT
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


class _GeneratingWorkflow(Workflow):
    steps = ["generate"]

    def generate(self) -> str:
        return self._call_llm("email", prompt="hi", system="Ты пишешь письма.")


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


def test_call_llm_combines_base_system_prompt_with_task_specific_one(stores):
    tasks_store, decisions_store = stores
    task = tasks_store.create_task(title="Test", task_type="email")
    captured = {}

    def capturing_caller(model_name, task_dict):
        captured.update(task_dict)
        return {"model_used": model_name, "text": "ok"}

    workflow = _GeneratingWorkflow(
        task["id"],
        llm_caller=capturing_caller,
        tasks_store=tasks_store,
        decisions_store=decisions_store,
    )
    workflow.run()

    assert captured["system"].startswith(BASE_SYSTEM_PROMPT)
    assert captured["system"].endswith("Ты пишешь письма.")
