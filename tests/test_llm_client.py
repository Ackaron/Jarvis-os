import pytest

from core import llm_client
from core.llm_client import (
    AnthropicNotConfiguredError,
    UnsupportedModelProviderError,
    call_anthropic,
)

ROUTING_CONFIG = {
    "models": {
        "claude-opus": {"api_provider": "anthropic", "api_model_id": "claude-opus-5"},
        "ollama-local": {"api_provider": "local"},
    }
}


class _FakeTextBlock:
    def __init__(self, text: str):
        self.type = "text"
        self.text = text


class _FakeResponse:
    def __init__(self, text: str):
        self.content = [_FakeTextBlock(text)]


class _FakeMessages:
    def __init__(self, response_text: str):
        self.response_text = response_text
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return _FakeResponse(self.response_text)


class _FakeAnthropicClient:
    def __init__(self, response_text: str = "hello"):
        self.messages = _FakeMessages(response_text)


def test_unsupported_provider_raises():
    with pytest.raises(UnsupportedModelProviderError):
        call_anthropic("ollama-local", {"prompt": "hi"}, config=ROUTING_CONFIG)


def test_unknown_model_raises():
    with pytest.raises(UnsupportedModelProviderError):
        call_anthropic("does-not-exist", {"prompt": "hi"}, config=ROUTING_CONFIG)


def test_missing_prompt_raises_value_error():
    client = _FakeAnthropicClient()
    with pytest.raises(ValueError):
        call_anthropic("claude-opus", {}, config=ROUTING_CONFIG, client=client)


def test_missing_api_key_raises_when_no_client_injected(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(AnthropicNotConfiguredError):
        call_anthropic("claude-opus", {"prompt": "hi"}, config=ROUTING_CONFIG)


def test_call_with_injected_fake_client_returns_text():
    client = _FakeAnthropicClient(response_text="Привет от модели")
    result = call_anthropic("claude-opus", {"prompt": "hi"}, config=ROUTING_CONFIG, client=client)
    assert result == {"model_used": "claude-opus-5", "text": "Привет от модели"}
    assert client.messages.last_kwargs["model"] == "claude-opus-5"
    assert client.messages.last_kwargs["messages"] == [{"role": "user", "content": "hi"}]


def test_get_anthropic_client_passes_base_url_when_set(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "http://localhost:20128")
    captured = {}

    class FakeAnthropicCls:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr("anthropic.Anthropic", FakeAnthropicCls)
    llm_client._get_anthropic_client()
    assert captured == {"api_key": "fake-key", "base_url": "http://localhost:20128"}


def test_get_anthropic_client_omits_base_url_when_unset(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    monkeypatch.delenv("ANTHROPIC_BASE_URL", raising=False)
    captured = {}

    class FakeAnthropicCls:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr("anthropic.Anthropic", FakeAnthropicCls)
    llm_client._get_anthropic_client()
    assert captured == {"api_key": "fake-key"}
