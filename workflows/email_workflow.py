"""Email Correspondence workflow (SPECIFICATION.md Workflow 3), built on
workflows.engine.Workflow. LLM calls go through core.llm_router with an
injectable caller (default: core.llm_client.call_anthropic) — see ADR-005.
"""

from __future__ import annotations

from typing import Callable, Optional

from core.llm_client import call_anthropic
from core.llm_router import execute_with_fallback, route_task
from workflows.engine import HumanInput, Workflow, cli_human_input

LLMCaller = Callable[[str, dict], dict]


class EmailWorkflow(Workflow):
    steps = [
        "intake_letter",
        "analyze_content",
        "collect_thesis",
        "generate_response",
        "review_response",
    ]

    def __init__(
        self,
        task_id: str,
        human_input: HumanInput = cli_human_input,
        llm_caller: LLMCaller = call_anthropic,
        **kwargs,
    ):
        super().__init__(task_id, human_input=human_input, **kwargs)
        self.llm_caller = llm_caller

    def _call_llm(self, task_type: str, prompt: str, system: str = "") -> str:
        decision = route_task(task_type)
        result = execute_with_fallback(
            decision, {"prompt": prompt, "system": system}, caller=self.llm_caller
        )
        return result["text"]

    def intake_letter(self) -> str:
        return self.ask("Вставь текст письма для анализа:")

    def analyze_content(self) -> str:
        letter = self.state["intake_letter"]
        return self._call_llm(
            "analysis",
            prompt=f"Проанализируй письмо и кратко укажи отправителя, тему и ключевой вопрос:\n\n{letter}",
            system="Ты помощник, который анализирует деловую переписку.",
        )

    def collect_thesis(self) -> str:
        return self.ask(
            "Какие тезисы ответа? (что подтвердить, какие цифры/сроки указать)"
        )

    def generate_response(self) -> str:
        letter = self.state["intake_letter"]
        analysis = self.state["analyze_content"]
        thesis = self.state["collect_thesis"]
        return self._call_llm(
            "email",
            prompt=(
                f"Письмо:\n{letter}\n\nАнализ:\n{analysis}\n\n"
                f"Тезисы ответа:\n{thesis}\n\nСоставь формальный деловой ответ на русском."
            ),
            system="Ты составляешь формальные деловые письма в корпоративном тоне.",
        )

    def review_response(self) -> str:
        draft = self.state["generate_response"]
        feedback = self.ask(f"Черновик ответа:\n{draft}\n\nПравки? (пусто = всё ок)")
        if not feedback:
            return draft

        reasoning = self.ask("Почему нужна эта правка?")
        self.record_correction(
            decision_type="content",
            field_changed="generate_response",
            original_value=draft,
            new_value=feedback,
            reasoning=reasoning,
        )
        return self._call_llm(
            "email",
            prompt=(
                f"Черновик:\n{draft}\n\nПравка от Виктора:\n{feedback}\n\n"
                "Перепиши письмо с учётом правки."
            ),
            system="Ты составляешь формальные деловые письма в корпоративном тоне.",
        )
