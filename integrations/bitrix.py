"""Bitrix24 connector — structural stub for Phase 0 (see ADR-004).

No real HTTP calls or credentials yet. Shapes match SPECIFICATION.md's
description of the Bitrix24 REST API usage (task sync, deadlines).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import core.env  # noqa: F401  side effect: loads .env


@dataclass
class BitrixTask:
    id: str
    title: str
    status: str
    deadline: Optional[str] = None


class BitrixClient:
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("BITRIX24_WEBHOOK_URL")

    def is_configured(self) -> bool:
        return bool(self.webhook_url)

    def list_tasks(self, **filters) -> list[BitrixTask]:
        raise NotImplementedError(
            "Bitrix24 integration is a structural stub (Phase 0, see ADR-004). "
            "Set BITRIX24_WEBHOOK_URL and implement the real REST call in Phase 1+."
        )

    def create_task(self, title: str, **fields) -> BitrixTask:
        raise NotImplementedError(
            "Bitrix24 integration is a structural stub (Phase 0, see ADR-004). "
            "Set BITRIX24_WEBHOOK_URL and implement the real REST call in Phase 1+."
        )
