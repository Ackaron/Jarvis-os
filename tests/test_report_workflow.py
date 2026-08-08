from pathlib import Path

import pytest

from core.context_engine import ContextEngine
from storage.decisions_store import DecisionStore
from storage.tasks_store import TaskStore
from tests.helpers import ScriptedHumanInput, fake_llm_caller
from workflows.report_workflow import ReportWorkflow


@pytest.fixture
def stores(tmp_path: Path):
    return (
        TaskStore(path=tmp_path / "tasks.json"),
        DecisionStore(path=tmp_path / "decisions.json"),
    )


def test_report_workflow_uses_existing_knowledge_base(tmp_path: Path, stores):
    tasks_store, decisions_store = stores
    kb_dir = tmp_path / "vault" / "knowledge_base" / "bootlegger"
    kb_dir.mkdir(parents=True)
    (kb_dir / "sales.md").write_text("Выручка за неделю: 500000", encoding="utf-8")
    context_engine = ContextEngine(vault_path=tmp_path / "vault")

    task = tasks_store.create_task(title="Weekly report", task_type="report")
    workflow = ReportWorkflow(
        task["id"],
        domain="bootlegger",
        topic="sales",
        human_input=ScriptedHumanInput([]),
        llm_caller=fake_llm_caller,
        context_engine=context_engine,
        tasks_store=tasks_store,
        decisions_store=decisions_store,
    )
    state = workflow.run()

    assert state["fetch_data"] == "Выручка за неделю: 500000"
    saved_path = tmp_path / "vault" / state["deliver_report"]
    assert saved_path.exists()
    assert saved_path.read_text(encoding="utf-8") == state["analyze_data"]


def test_report_workflow_asks_for_manual_data_when_kb_missing(tmp_path: Path, stores):
    tasks_store, decisions_store = stores
    context_engine = ContextEngine(vault_path=tmp_path / "vault")

    task = tasks_store.create_task(title="Ad-hoc report", task_type="report")
    workflow = ReportWorkflow(
        task["id"],
        domain="bootlegger",
        topic="does_not_exist",
        human_input=ScriptedHumanInput(["Вручную вставленные данные"]),
        llm_caller=fake_llm_caller,
        context_engine=context_engine,
        tasks_store=tasks_store,
        decisions_store=decisions_store,
    )
    state = workflow.run()
    assert state["fetch_data"] == "Вручную вставленные данные"
