"""Shared test doubles for workflow tests."""

from __future__ import annotations

from typing import Any, Optional


class ScriptedHumanInput:
    """Fake human_input: returns canned answers in order, ignoring the prompt."""

    def __init__(self, responses: list[Any]):
        self._responses = list(responses)
        self.prompts_seen: list[str] = []

    def __call__(self, prompt: str, context: Optional[dict] = None) -> Any:
        self.prompts_seen.append(prompt)
        return self._responses.pop(0)


def fake_llm_caller(model_name: str, task: dict) -> dict:
    return {"model_used": model_name, "text": f"[{model_name}] {task['prompt'][:40]}"}
