"""Free-slot scheduling logic (SPECIFICATION.md -> Calendar/Scheduling).
Works against any list of busy intervals via dependency injection — doesn't
need a real Google Calendar connection (see ADR-006);
integrations.google_calendar supplies real events once OAuth is configured.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence


@dataclass
class BusyInterval:
    start: datetime
    end: datetime


@dataclass
class FreeSlot:
    start: datetime
    end: datetime

    @property
    def duration_seconds(self) -> float:
        return (self.end - self.start).total_seconds()


def find_free_slots(
    window_start: datetime,
    window_end: datetime,
    busy_intervals: Sequence[BusyInterval],
    min_duration_seconds: int = 0,
) -> list[FreeSlot]:
    if window_start >= window_end:
        return []

    relevant_busy = sorted(
        (b for b in busy_intervals if b.end > window_start and b.start < window_end),
        key=lambda b: b.start,
    )

    slots: list[FreeSlot] = []
    cursor = window_start
    for busy in relevant_busy:
        busy_start = max(busy.start, window_start)
        busy_end = min(busy.end, window_end)
        if busy_start > cursor:
            slots.append(FreeSlot(cursor, busy_start))
        cursor = max(cursor, busy_end)

    if cursor < window_end:
        slots.append(FreeSlot(cursor, window_end))

    return [s for s in slots if s.duration_seconds >= min_duration_seconds]
