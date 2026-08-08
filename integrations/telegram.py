"""Telegram Bot connector — structural stub for Phase 0 (see ADR-004).

No real Bot API calls or token yet. The bot server (/new_task, /status,
/approve handlers from JARVIS_OS_ARCHITECTURE.md) is Phase 2 work; this is
just the outbound client Jarvis will use to send messages/notifications.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import core.env  # noqa: F401  side effect: loads .env


@dataclass
class TelegramMessage:
    chat_id: str
    text: str


class TelegramClient:
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")

    def is_configured(self) -> bool:
        return bool(self.bot_token)

    def send_message(self, chat_id: str, text: str) -> TelegramMessage:
        raise NotImplementedError(
            "Telegram integration is a structural stub (Phase 0, see ADR-004). "
            "Set TELEGRAM_BOT_TOKEN and implement the real Bot API call in Phase 2+."
        )
