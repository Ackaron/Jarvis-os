"""Interface-agnostic workflow engine (see ADR-005).

Steps get a `human_input` callback injected instead of talking to a specific
UI. Phase 1 defaults to a blocking CLI prompt; Phase 2 will plug a Telegram/Web
callback with the same signature into the same workflow classes — no rewrite.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from core.llm_dispatch import call_model
from core.llm_router import execute_with_fallback, route_task
from core.mentoring import explain_task
from core.system_prompt import with_base
from storage.decisions_store import DecisionStore
from storage.tasks_store import TaskStore

HumanInput = Callable[[str, Optional[dict]], Any]
LLMCaller = Callable[[str, dict], dict]


def cli_human_input(prompt: str, context: Optional[dict] = None) -> Any:
    """Default human_input: blocking console prompt."""
    return input(f"{prompt}\n> ")


@dataclass
class StepResult:
    name: str
    output: Any


class Workflow:
    """Subclasses set `steps` to an ordered list of their own method names.
    Each step is called with no arguments and may read prior outputs from
    `self.state[step_name]`."""

    steps: list[str] = []

    def __init__(
        self,
        task_id: str,
        human_input: HumanInput = cli_human_input,
        llm_caller: LLMCaller = call_model,
        tasks_store: Optional[TaskStore] = None,
        decisions_store: Optional[DecisionStore] = None,
    ):
        self.task_id = task_id
        self.human_input = human_input
        self.llm_caller = llm_caller
        self.tasks_store = tasks_store or TaskStore()
        self.decisions_store = decisions_store or DecisionStore()
        self.state: dict[str, Any] = {}
        self.history: list[StepResult] = []

    def ask(self, prompt: str, context: Optional[dict] = None) -> Any:
        return self.human_input(prompt, context or {})

    def _call_llm(self, task_type: str, prompt: str, system: str = "") -> str:
        """Every real generation call goes through here so the base system
        prompt (core.system_prompt.BASE_SYSTEM_PROMPT) is applied uniformly —
        see the injected-prompt discussion that led to ADR-010."""
        decision = route_task(task_type)
        result = execute_with_fallback(
            decision,
            {"prompt": prompt, "system": with_base(system)},
            caller=self.llm_caller,
        )
        return result["text"]

    def record_correction(
        self,
        decision_type: str,
        field_changed: str,
        original_value: Any,
        new_value: Any,
        reasoning: str,
    ) -> dict:
        return self.decisions_store.log_decision(
            task_id=self.task_id,
            decision_type=decision_type,
            field_changed=field_changed,
            original_value=original_value,
            new_value=new_value,
            reasoning=reasoning,
        )

    def run(self) -> dict:
        self.tasks_store.update_task(self.task_id, status="in_progress")
        for step_name in self.steps:
            output = getattr(self, step_name)()
            self.history.append(StepResult(name=step_name, output=output))
            self.state[step_name] = output
        self.tasks_store.update_task(self.task_id, status="awaiting_review")
        return self.state

    def complete(self) -> dict:
        iterations = len(self.decisions_store.list_decisions(task_id=self.task_id))
        self.tasks_store.update_task(
            self.task_id, status="completed", iterations_count=iterations
        )
        return self.state

    def explain(self) -> str:
        """Mentoring Mode: why did the last run of this workflow make its
        corrections? Subclasses with a stakeholder concept may override to
        pass richer context."""
        return explain_task(self.task_id, decisions_store=self.decisions_store)
