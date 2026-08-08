import pytest

from integrations.bitrix import BitrixClient
from integrations.fusionpos import FusionPOSClient
from integrations.telegram import TelegramClient


def test_bitrix_not_configured_without_env(monkeypatch):
    monkeypatch.delenv("BITRIX24_WEBHOOK_URL", raising=False)
    client = BitrixClient()
    assert client.is_configured() is False


def test_bitrix_configured_with_explicit_url():
    client = BitrixClient(webhook_url="https://example.bitrix24.ru/rest/1/xxx/")
    assert client.is_configured() is True


def test_bitrix_list_tasks_raises_not_implemented():
    client = BitrixClient(webhook_url="https://example.bitrix24.ru/rest/1/xxx/")
    with pytest.raises(NotImplementedError):
        client.list_tasks()


def test_fusionpos_not_configured_without_env(monkeypatch):
    monkeypatch.delenv("FUSIONPOS_API_KEY", raising=False)
    client = FusionPOSClient()
    assert client.is_configured() is False


def test_fusionpos_get_orders_raises_not_implemented():
    client = FusionPOSClient(api_key="fake-key")
    with pytest.raises(NotImplementedError):
        client.get_orders()


def test_telegram_not_configured_without_env(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    client = TelegramClient()
    assert client.is_configured() is False


def test_telegram_send_message_raises_not_implemented():
    client = TelegramClient(bot_token="fake-token")
    with pytest.raises(NotImplementedError):
        client.send_message("123", "hello")
