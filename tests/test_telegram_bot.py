from pathlib import Path

import pytest

from interfaces.telegram_bot import TelegramDispatcher
from storage.tasks_store import TaskStore
from tests.helpers import fake_llm_caller


@pytest.fixture
def tasks_store(tmp_path: Path) -> TaskStore:
    return TaskStore(path=tmp_path / "tasks.json")


def _make_dispatcher(tasks_store: TaskStore):
    sent = []

    def fake_send(chat_id: str, text: str) -> None:
        sent.append((chat_id, text))

    dispatcher = TelegramDispatcher(
        send_message=fake_send, tasks_store=tasks_store, llm_caller=fake_llm_caller
    )
    return dispatcher, sent


def test_new_task_starts_email_workflow_end_to_end(tasks_store: TaskStore):
    dispatcher, sent = _make_dispatcher(tasks_store)

    dispatcher.handle_message("chat1", "/new_task Письмо в УК про статус резидента")
    assert "chat1" in dispatcher._sessions

    session = dispatcher._sessions["chat1"]
    session.inbox.put("Письмо от УК про статус резидента")  # intake_letter
    session.inbox.put("Подтвердить контракт активен")  # collect_thesis
    session.inbox.put("")  # review_response: no correction

    session.thread.join(timeout=5)

    assert "chat1" not in dispatcher._sessions
    assert any("Начинаю" in text for _, text in sent)
    assert any("готова к проверке" in text for _, text in sent)

    task_id = sent[0][1].split("task ")[-1].rstrip(")")
    assert tasks_store.get_task(task_id)["status"] == "awaiting_review"


def test_message_without_active_session_gets_a_hint(tasks_store: TaskStore):
    dispatcher, sent = _make_dispatcher(tasks_store)
    dispatcher.handle_message("chat2", "просто текст без /new_task")
    assert any("/new_task" in text for _, text in sent)


def test_status_command_reports_task_status(tasks_store: TaskStore):
    dispatcher, sent = _make_dispatcher(tasks_store)
    task = tasks_store.create_task(title="T", task_type="email")

    dispatcher.handle_message("chat3", f"/status {task['id']}")
    assert any("queued" in text for _, text in sent)


def test_status_command_unknown_task(tasks_store: TaskStore):
    dispatcher, sent = _make_dispatcher(tasks_store)
    dispatcher.handle_message("chat4", "/status does-not-exist")
    assert any("не найдена" in text for _, text in sent)


def test_unsupported_task_type_reports_gracefully(tasks_store: TaskStore):
    dispatcher, sent = _make_dispatcher(tasks_store)
    dispatcher.handle_message("chat5", "/new_task просто зайди и посмотри")
    assert "chat5" not in dispatcher._sessions
    assert any("не умею" in text for _, text in sent)
