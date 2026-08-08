import pytest

from core import ollama_client
from core.ollama_client import UnsupportedModelProviderError, call_ollama

ROUTING_CONFIG = {
    "models": {
        "ollama-local": {"api_provider": "local", "api_model_id": "llama3.1"},
        "claude-opus": {"api_provider": "anthropic"},
    }
}


class _FakeResponse:
    def __init__(self, text: str):
        self._text = text
        self.raised = False

    def raise_for_status(self) -> None:
        self.raised = True

    def json(self) -> dict:
        return {"message": {"content": self._text}}


class _FakeHttpClient:
    def __init__(self, response_text: str = "hello"):
        self.response_text = response_text
        self.last_call = None
        self.closed = False

    def post(self, path: str, json: dict):
        self.last_call = (path, json)
        return _FakeResponse(self.response_text)

    def close(self) -> None:
        self.closed = True


def test_unsupported_provider_raises():
    with pytest.raises(UnsupportedModelProviderError):
        call_ollama("claude-opus", {"prompt": "hi"}, config=ROUTING_CONFIG)


def test_unknown_model_raises():
    with pytest.raises(UnsupportedModelProviderError):
        call_ollama("does-not-exist", {"prompt": "hi"}, config=ROUTING_CONFIG)


def test_missing_prompt_raises_value_error():
    client = _FakeHttpClient()
    with pytest.raises(ValueError):
        call_ollama("ollama-local", {}, config=ROUTING_CONFIG, client=client)


def test_call_with_injected_fake_client_returns_text():
    client = _FakeHttpClient(response_text="Привет от Ollama")
    result = call_ollama("ollama-local", {"prompt": "hi"}, config=ROUTING_CONFIG, client=client)
    assert result == {"model_used": "llama3.1", "text": "Привет от Ollama"}
    path, payload = client.last_call
    assert path == "/api/chat"
    assert payload["model"] == "llama3.1"
    assert payload["messages"] == [{"role": "user", "content": "hi"}]
    assert client.closed is False  # injected clients aren't auto-closed


def test_system_prompt_included_when_provided():
    client = _FakeHttpClient()
    call_ollama(
        "ollama-local", {"prompt": "hi", "system": "be terse"}, config=ROUTING_CONFIG, client=client
    )
    _, payload = client.last_call
    assert payload["messages"][0] == {"role": "system", "content": "be terse"}


def test_default_http_client_uses_ollama_base_url_env(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:9999")
    client = ollama_client._get_http_client()
    assert str(client.base_url) == "http://localhost:9999"
    client.close()


def test_default_http_client_falls_back_to_default_url(monkeypatch):
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    client = ollama_client._get_http_client()
    assert str(client.base_url) == ollama_client.DEFAULT_OLLAMA_BASE_URL
    client.close()
