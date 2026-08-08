"""Telegram-backed dispatcher for workflows.engine (ADR-005/ADR-006).

This does NOT talk to the real Telegram Bot API — integrations.telegram is
still a structural stub pending TELEGRAM_BOT_TOKEN (ADR-004). What's real
here is the *dispatch logic*: routing an incoming (chat_id, text) message to
either "start a new workflow" or "answer a workflow's pending question",
reusing the exact same HumanInput contract every other Phase 1 interface
uses — no python-telegram-bot dependency needed for this part. Only the
actual Bot API polling loop needs the real library + token, and is
deliberately out of scope until Viktor provides one.
"""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass, field
from typing import Callable, Optional

from core.intent_router import classify_intent
from core.llm_client import call_anthropic
from integrations.telegram import TelegramClient
from storage.tasks_store import TaskStore
from workflows.email_workflow import EmailWorkflow
from workflows.presentation_workflow import PresentationWorkflow
from workflows.report_workflow import ReportWorkflow

SendMessage = Callable[[str, str], None]
LLMCaller = Callable[[str, dict], dict]

WORKFLOW_BY_TASK_TYPE = {
    "email": EmailWorkflow,
    "report": ReportWorkflow,
    "presentation": PresentationWorkflow,
}


def _default_send_message(chat_id: str, text: str) -> None:
    """Real send — raises NotImplementedError until TELEGRAM_BOT_TOKEN exists."""
    TelegramClient().send_message(chat_id, text)


class TelegramHumanInput:
    """A HumanInput implementation backed by a per-chat queue: `ask()` sends
    the prompt via `send_message`, then blocks until the dispatcher pushes
    the chat's next incoming text into the queue."""

    def __init__(
        self,
        chat_id: str,
        send_message: SendMessage,
        inbox: "queue.Queue[str]",
        timeout: Optional[float] = None,
    ):
        self.chat_id = chat_id
        self.send_message = send_message
        self.inbox = inbox
        self.timeout = timeout

    def __call__(self, prompt: str, context: Optional[dict] = None) -> str:
        self.send_message(self.chat_id, prompt)
        return self.inbox.get(timeout=self.timeout)


@dataclass
class PendingSession:
    task_id: str
    inbox: "queue.Queue[str]" = field(default_factory=queue.Queue)
    thread: Optional[threading.Thread] = None


class TelegramDispatcher:
    """Routes incoming (chat_id, text) pairs: `/new_task <desc>` starts a
    workflow in a background thread; any other message is delivered to that
    chat's currently-running workflow, if one is waiting on input."""

    def __init__(
        self,
        send_message: SendMessage = _default_send_message,
        tasks_store: Optional[TaskStore] = None,
        llm_caller: LLMCaller = call_anthropic,
    ):
        self.send_message = send_message
        self.tasks_store = tasks_store or TaskStore()
        self.llm_caller = llm_caller
        self._sessions: dict[str, PendingSession] = {}
        self._lock = threading.Lock()

    def handle_message(self, chat_id: str, text: str) -> None:
        if text.startswith("/new_task"):
            description = text[len("/new_task") :].strip()
            self._start_workflow(chat_id, description)
            return

        if text.startswith("/status"):
            task_id = text[len("/status") :].strip()
            self._send_status(chat_id, task_id)
            return

        with self._lock:
            session = self._sessions.get(chat_id)
        if session is None:
            self.send_message(chat_id, "Нет активной задачи. Начни с /new_task <описание>.")
            return
        session.inbox.put(text)

    def _send_status(self, chat_id: str, task_id: str) -> None:
        try:
            task = self.tasks_store.get_task(task_id)
        except KeyError:
            self.send_message(chat_id, f"Задача {task_id} не найдена.")
            return
        self.send_message(chat_id, f"Статус задачи {task_id}: {task['status']}")

    def _start_workflow(self, chat_id: str, description: str) -> None:
        intent = classify_intent(description)
        workflow_cls = WORKFLOW_BY_TASK_TYPE.get(intent.task_type)
        if workflow_cls is None:
            self.send_message(
                chat_id,
                f"Пока не умею запускать воркфлоу для типа '{intent.task_type}' через Telegram.",
            )
            return

        task = self.tasks_store.create_task(title=description, task_type=intent.task_type)
        session = PendingSession(task_id=task["id"])
        with self._lock:
            self._sessions[chat_id] = session

        human_input = TelegramHumanInput(chat_id, self.send_message, session.inbox)
        workflow_kwargs: dict = {"tasks_store": self.tasks_store, "llm_caller": self.llm_caller}
        if workflow_cls is PresentationWorkflow:
            workflow_kwargs["stakeholder_name"] = intent.stakeholder or "Unknown"
        elif workflow_cls is ReportWorkflow:
            workflow_kwargs["domain"] = intent.domain or "general"
            workflow_kwargs["topic"] = "general"

        thread = threading.Thread(
            target=self._run_workflow,
            args=(chat_id, task["id"], workflow_cls, human_input, workflow_kwargs),
            daemon=True,
        )
        session.thread = thread
        thread.start()
        self.send_message(chat_id, f"Начинаю: {description} (task {task['id']})")

    def _run_workflow(self, chat_id, task_id, workflow_cls, human_input, workflow_kwargs) -> None:
        workflow = workflow_cls(task_id, human_input=human_input, **workflow_kwargs)
        workflow.run()
        self.send_message(chat_id, f"Задача {task_id} готова к проверке (/status {task_id}).")
        with self._lock:
            self._sessions.pop(chat_id, None)
