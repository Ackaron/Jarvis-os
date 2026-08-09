"""Presentation workflow (SPECIFICATION.md Workflow 1). Phase 1 scope produces
a structured slide-by-slide text artifact saved to the vault, not a rendered
.pptx binary — real file rendering (python-pptx) is Phase 2+ Output Generator
work, out of ADR-005's scope. Quality Assurance is wired into the structure
approval step, matching the SPEC's own worked example (Трутнев presentations).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from core.context_engine import ContextEngine
from core.llm_dispatch import call_model
from core.mentoring import explain_task
from core.quality_assurance import format_qa_prompt
from workflows.engine import HumanInput, LLMCaller, Workflow, cli_human_input


class PresentationWorkflow(Workflow):
    steps = [
        "confirm_stakeholder",
        "collect_data",
        "propose_structure",
        "approve_structure",
        "fill_content",
        "finalize",
    ]

    def __init__(
        self,
        task_id: str,
        stakeholder_name: str,
        human_input: HumanInput = cli_human_input,
        llm_caller: LLMCaller = call_model,
        context_engine: Optional[ContextEngine] = None,
        **kwargs,
    ):
        super().__init__(task_id, human_input=human_input, llm_caller=llm_caller, **kwargs)
        self.stakeholder_name = stakeholder_name
        self.context_engine = context_engine or ContextEngine()

    def confirm_stakeholder(self) -> Optional[dict]:
        return self.context_engine.get_stakeholder(self.stakeholder_name)

    def collect_data(self) -> str:
        return self.ask(f"Вставь данные для презентации ({self.stakeholder_name}):")

    def propose_structure(self) -> str:
        stakeholder = self.state["confirm_stakeholder"]
        focus = (stakeholder or {}).get("metadata", {}).get("focus_areas", [])
        data = self.state["collect_data"]
        return self._call_llm(
            "presentation",
            prompt=(
                f"Данные:\n{data}\n\nФокус стейкхолдера ({self.stakeholder_name}): {focus}\n\n"
                "Предложи структуру презентации по слайдам (заголовки + краткое содержание каждого)."
            ),
            system="Ты помощник, который проектирует структуру деловых презентаций.",
        )

    def approve_structure(self) -> str:
        structure = self.state["propose_structure"]
        stakeholder = self.state["confirm_stakeholder"]
        qa_prompt = format_qa_prompt(stakeholder)
        feedback = self.ask(
            f"Структура:\n{structure}\n\n{qa_prompt}\n\nПравки? (пусто = одобряю)"
        )
        if not feedback:
            return structure

        reasoning = self.ask("Почему эта правка?")
        self.record_correction(
            decision_type="structure",
            field_changed="propose_structure",
            original_value=structure,
            new_value=feedback,
            reasoning=reasoning,
        )
        return self._call_llm(
            "presentation",
            prompt=f"Структура:\n{structure}\n\nПравка:\n{feedback}\n\nОбнови структуру.",
            system="Ты помощник, который проектирует структуру деловых презентаций.",
        )

    def fill_content(self) -> str:
        structure = self.state["approve_structure"]
        data = self.state["collect_data"]
        return self._call_llm(
            "presentation",
            prompt=f"Структура:\n{structure}\n\nДанные:\n{data}\n\nЗаполни каждый слайд текстом на основе данных.",
            system="Ты составляешь финальный текст слайдов деловой презентации.",
        )

    def finalize(self) -> str:
        content = self.state["fill_content"]
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        relative_path = f"templates/presentations/{timestamp}_{self.task_id}.md"
        self.context_engine.vault.write_note(relative_path, content)

        stakeholder = self.state["confirm_stakeholder"]
        current_count = (stakeholder or {}).get("metadata", {}).get("interaction_count", 0)
        self.context_engine.update_stakeholder_profile(
            self.stakeholder_name, interaction_count=current_count + 1
        )
        return relative_path

    def explain(self) -> str:
        return explain_task(
            self.task_id,
            stakeholder=self.state.get("confirm_stakeholder"),
            decisions_store=self.decisions_store,
        )
