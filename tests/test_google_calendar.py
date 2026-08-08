from datetime import datetime, timezone

import pytest

from integrations.google_calendar import GoogleCalendarClient


def test_not_configured_without_env(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    client = GoogleCalendarClient()
    assert client.is_configured() is False


def test_configured_with_explicit_credentials():
    client = GoogleCalendarClient(client_id="id", client_secret="secret")
    assert client.is_configured() is True


def test_list_events_raises_not_implemented():
    client = GoogleCalendarClient(client_id="id", client_secret="secret")
    with pytest.raises(NotImplementedError):
        client.list_events(datetime.now(timezone.utc), datetime.now(timezone.utc))
