"""Report workflow (SPECIFICATION.md Workflow 2). Phase 1 scope: data comes
from core.context_engine.get_knowledge() or manual input — live FusionPOS/
Bitrix pull is still a stub (ADR-004), so this asks Viktor for data instead of
pretending to fetch it automatically.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Optional

from core.context_engine import ContextEngine
from core.llm_client import call_anthropic
from core.llm_router import execute_with_fallback, route_task
from workflows.engine import HumanInput, Workflow, cli_human_input

LLMCaller = Callable[[str, dict], dict]


class ReportWorkflow(Workflow):
    steps = ["fetch_data", "analyze_data", "deliver_report"]

    def __init__(
        self,
        task_id: str,
        domain: str,
        topic: str,
        human_input: HumanInput = cli_human_input,
        llm_caller: LLMCaller = call_anthropic,
        context_engine: Optional[ContextEngine] = None,
        **kwargs,
    ):
        super().__init__(task_id, human_input=human_input, **kwargs)
        self.domain = domain
        self.topic = topic
        self.llm_caller = llm_caller
        self.context_engine = context_engine or ContextEngine()

    def _call_llm(self, task_type: str, prompt: str, system: str = "") -> str:
        decision = route_task(task_type)
        result = execute_with_fallback(
            decision, {"prompt": prompt, "system": system}, caller=self.llm_caller
        )
        return result["text"]

    def fetch_data(self) -> str:
        data = self.context_engine.get_knowledge(self.domain, self.topic)
        if data is None:
            data = self.ask(
                f"В knowledge_base нет '{self.domain}/{self.topic}'. Вставь данные вручную:"
            )
        return data

    def analyze_data(self) -> str:
        data = self.state["fetch_data"]
        return self._call_llm(
            "report",
            prompt=f"Проанализируй данные и сделай краткую сводку с выводами:\n\n{data}",
            system="Ты аналитик, который делает деловые отчёты.",
        )

    def deliver_report(self) -> str:
        analysis = self.state["analyze_data"]
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        relative_path = f"knowledge_base/{self.domain}/reports/{timestamp}_{self.task_id}.md"
        self.context_engine.vault.write_note(relative_path, analysis)
        return relative_path
