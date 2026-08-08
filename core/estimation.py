"""Time estimation from historical completed tasks (SPECIFICATION.md ->
Time Estimation & Historical Data). Falls back to a conservative default
when there's no history yet for a given task_type.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Optional

from storage.tasks_store import TaskStore

DEFAULT_ESTIMATE_SECONDS = 1800  # 30 min — used when there's no history at all
DEFAULT_CONFIDENCE = 0.3
MIN_SAMPLE_SIZE_FOR_HIGH_CONFIDENCE = 3


@dataclass
class Estimate:
    task_type: str
    estimated_seconds: int
    confidence: float
    sample_size: int


def estimate_duration(task_type: str, tasks_store: Optional[TaskStore] = None) -> Estimate:
    tasks_store = tasks_store or TaskStore()
    completed = [
        t
        for t in tasks_store.list_tasks(status="completed")
        if t.get("task_type") == task_type and t.get("time_actual_seconds")
    ]

    if not completed:
        return Estimate(
            task_type=task_type,
            estimated_seconds=DEFAULT_ESTIMATE_SECONDS,
            confidence=DEFAULT_CONFIDENCE,
            sample_size=0,
        )

    durations = [t["time_actual_seconds"] for t in completed]
    avg = mean(durations)

    if len(durations) < MIN_SAMPLE_SIZE_FOR_HIGH_CONFIDENCE:
        confidence = 0.5
    else:
        variance_ratio = (pstdev(durations) / avg) if avg else 0.0
        confidence = max(0.5, min(0.95, 1 - variance_ratio))

    return Estimate(
        task_type=task_type,
        estimated_seconds=round(avg),
        confidence=round(confidence, 2),
        sample_size=len(durations),
    )
