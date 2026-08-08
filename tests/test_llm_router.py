import pytest

from core.llm_router import (
    AllModelsFailedError,
    call_model,
    execute_with_fallback,
    route_task,
)

ROUTING_CONFIG = {
    "defaults": {
        "primary_model": "claude-sonnet",
        "fallback_chain": ["ollama-local"],
    },
    "routing_rules": {
        "presentation": {
            "primary": "claude-opus",
            "fallback": ["claude-sonnet"],
            "reason": "needs creative synthesis",
        },
        "analysis": {
            "primary": "claude-opus",
            "fallback": False,
            "reason": "number accuracy non-negotiable",
        },
        "email": {
            "primary": "claude-sonnet",
            "observer": "ollama-mistral",
        },
    },
}


def test_known_rule_resolves_primary_and_fallback():
    decision = route_task("presentation", ROUTING_CONFIG)
    assert decision.primary_model == "claude-opus"
    assert decision.chain == ["claude-opus", "claude-sonnet"]


def test_unknown_task_type_falls_back_to_defaults():
    decision = route_task("some_new_task_type", ROUTING_CONFIG)
    assert decision.primary_model == "claude-sonnet"
    assert decision.chain == ["claude-sonnet", "ollama-local"]


def test_fallback_false_disables_chain():
    decision = route_task("analysis", ROUTING_CONFIG)
    assert decision.fallback_allowed is False
    assert decision.chain == ["claude-opus"]


def test_observer_is_carried_through():
    decision = route_task("email", ROUTING_CONFIG)
    assert decision.observer == "ollama-mistral"


def test_call_model_stub_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        call_model("claude-opus", {"task_type": "presentation"})


def test_execute_with_fallback_raises_after_exhausting_chain():
    decision = route_task("presentation", ROUTING_CONFIG)
    with pytest.raises(AllModelsFailedError):
        execute_with_fallback(decision, {"task_type": "presentation"})


def test_execute_with_fallback_succeeds_with_working_caller():
    decision = route_task("presentation", ROUTING_CONFIG)
    calls = []

    def fake_caller(model_name: str, task: dict) -> dict:
        calls.append(model_name)
        if model_name != "claude-sonnet":
            raise RuntimeError("simulated failure")
        return {"model_used": model_name}

    result = execute_with_fallback(decision, {"task_type": "presentation"}, caller=fake_caller)
    assert result == {"model_used": "claude-sonnet"}
    assert calls == ["claude-opus", "claude-sonnet"]
