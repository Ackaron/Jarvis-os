import pytest

from core.llm_dispatch import UnknownProviderError, call_model

ROUTING_CONFIG = {
    "models": {
        "ollama-local": {"api_provider": "local", "api_model_id": "llama3.1"},
        "claude-opus": {"api_provider": "anthropic", "api_model_id": "claude-opus-5"},
        "mystery-model": {"api_provider": "carrier-pigeon"},
    }
}


def test_dispatches_to_ollama_caller(monkeypatch):
    calls = []

    def fake_ollama(model_name, task, config=None):
        calls.append((model_name, task, config))
        return {"model_used": model_name, "text": "from ollama"}

    monkeypatch.setattr("core.llm_dispatch.PROVIDER_CALLERS", {"local": fake_ollama})
    result = call_model("ollama-local", {"prompt": "hi"}, config=ROUTING_CONFIG)
    assert result == {"model_used": "ollama-local", "text": "from ollama"}
    assert calls[0][0] == "ollama-local"


def test_dispatches_to_anthropic_caller(monkeypatch):
    def fake_anthropic(model_name, task, config=None):
        return {"model_used": model_name, "text": "from anthropic"}

    monkeypatch.setattr("core.llm_dispatch.PROVIDER_CALLERS", {"anthropic": fake_anthropic})
    result = call_model("claude-opus", {"prompt": "hi"}, config=ROUTING_CONFIG)
    assert result == {"model_used": "claude-opus", "text": "from anthropic"}


def test_unknown_model_raises():
    with pytest.raises(UnknownProviderError):
        call_model("does-not-exist", {"prompt": "hi"}, config=ROUTING_CONFIG)


def test_unregistered_provider_raises(monkeypatch):
    with pytest.raises(UnknownProviderError):
        call_model("mystery-model", {"prompt": "hi"}, config=ROUTING_CONFIG)


def test_call_model_uses_real_ollama_local_by_default():
    """Sanity check against the real vault/system/routing.yaml (post-ADR-007:
    Ollama is primary), using an injected caller so no network call happens."""
    from core.llm_dispatch import call_model as real_call_model

    calls = []

    def fake_caller(model_name, task, config=None):
        calls.append(model_name)
        return {"model_used": model_name, "text": "ok"}

    import core.llm_dispatch as dispatch_module

    original = dispatch_module.PROVIDER_CALLERS["local"]
    dispatch_module.PROVIDER_CALLERS["local"] = fake_caller
    try:
        result = real_call_model("ollama-local", {"prompt": "hi"})
    finally:
        dispatch_module.PROVIDER_CALLERS["local"] = original

    assert result["text"] == "ok"
    assert calls == ["ollama-local"]
