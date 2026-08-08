"""Google Calendar connector — structural stub for Phase 2 (see ADR-006).

No real OAuth/API calls yet. Shapes match SPECIFICATION.md's mention of the
Google Calendar API + OAuth 2.0 for scheduling and free-slot detection.
core/scheduler.py works against any list of events, so it doesn't need this
to be real to be useful today.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CalendarEvent:
    id: str
    title: str
    start_time: datetime
    end_time: datetime


class GoogleCalendarClient:
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id or os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("GOOGLE_CLIENT_SECRET")

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def list_events(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        raise NotImplementedError(
            "Google Calendar integration is a structural stub (Phase 2, see ADR-006). "
            "Set GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET and implement real OAuth + "
            "API calls before this can return live events."
        )
