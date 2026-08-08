from pathlib import Path

import pytest

from core.context_engine import ContextEngine
from storage.decisions_store import DecisionStore
from storage.tasks_store import TaskStore
from tests.helpers import ScriptedHumanInput, fake_llm_caller
from workflows.presentation_workflow import PresentationWorkflow


@pytest.fixture
def stores(tmp_path: Path):
    return (
        TaskStore(path=tmp_path / "tasks.json"),
        DecisionStore(path=tmp_path / "decisions.json"),
    )


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    vault_dir = tmp_path / "vault"
    stakeholders_dir = vault_dir / "stakeholders"
    stakeholders_dir.mkdir(parents=True)
    (stakeholders_dir / "Трутнев.md").write_text(
        "---\nfocus_areas: [Инвестиции, Продукты]\ninteraction_count: 4\n---\n"
        "Заметки.\n",
        encoding="utf-8",
    )
    return vault_dir


def test_presentation_workflow_no_corrections_updates_stakeholder(vault: Path, stores):
    tasks_store, decisions_store = stores
    context_engine = ContextEngine(vault_path=vault)
    task = tasks_store.create_task(title="Презентация резидентов", task_type="presentation")

    human_input = ScriptedHumanInput(
        [
            "Компания X: Investment $75M",  # collect_data
            "",  # approve_structure: no corrections
        ]
    )
    workflow = PresentationWorkflow(
        task["id"],
        stakeholder_name="Трутнев",
        human_input=human_input,
        llm_caller=fake_llm_caller,
        context_engine=context_engine,
        tasks_store=tasks_store,
        decisions_store=decisions_store,
    )
    state = workflow.run()
    workflow.complete()

    assert state["confirm_stakeholder"]["metadata"]["focus_areas"] == ["Инвестиции", "Продукты"]
    saved_path = vault / state["finalize"]
    assert saved_path.exists()

    updated = context_engine.get_stakeholder("Трутнев")
    assert updated["metadata"]["interaction_count"] == 5


def test_presentation_workflow_with_correction_logs_decision_and_explains(vault: Path, stores):
    tasks_store, decisions_store = stores
    context_engine = ContextEngine(vault_path=vault)
    task = tasks_store.create_task(title="Презентация инвесторов", task_type="presentation")

    human_input = ScriptedHumanInput(
        [
            "Компания Y данные",  # collect_data
            "Убрать слайд про партнёров",  # approve_structure feedback
            "Трутнев не интересуется партнёрами",  # reasoning
        ]
    )
    workflow = PresentationWorkflow(
        task["id"],
        stakeholder_name="Трутнев",
        human_input=human_input,
        llm_caller=fake_llm_caller,
        context_engine=context_engine,
        tasks_store=tasks_store,
        decisions_store=decisions_store,
    )
    workflow.run()

    decisions = decisions_store.list_decisions(task_id=task["id"])
    assert len(decisions) == 1
    assert decisions[0]["reasoning"] == "Трутнев не интересуется партнёрами"

    explanation = workflow.explain()
    assert "Трутнев не интересуется партнёрами" in explanation
    assert "Инвестиции" in explanation


def test_presentation_workflow_unknown_stakeholder_uses_no_focus(vault: Path, stores):
    tasks_store, decisions_store = stores
    context_engine = ContextEngine(vault_path=vault)
    task = tasks_store.create_task(title="Презентация для нового", task_type="presentation")

    human_input = ScriptedHumanInput(["Данные", ""])
    workflow = PresentationWorkflow(
        task["id"],
        stakeholder_name="Неизвестный",
        human_input=human_input,
        llm_caller=fake_llm_caller,
        context_engine=context_engine,
        tasks_store=tasks_store,
        decisions_store=decisions_store,
    )
    state = workflow.run()
    assert state["confirm_stakeholder"] is None
