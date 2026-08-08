from datetime import datetime, timedelta, timezone

from core.scheduler import BusyInterval, find_free_slots

BASE = datetime(2026, 8, 10, 9, 0, tzinfo=timezone.utc)


def _at(hours: float) -> datetime:
    return BASE + timedelta(hours=hours)


def test_no_busy_intervals_returns_whole_window():
    slots = find_free_slots(_at(0), _at(8), [])
    assert len(slots) == 1
    assert slots[0].start == _at(0)
    assert slots[0].end == _at(8)


def test_single_busy_interval_splits_window_in_two():
    busy = [BusyInterval(_at(2), _at(3))]
    slots = find_free_slots(_at(0), _at(8), busy)
    assert len(slots) == 2
    assert slots[0].start == _at(0) and slots[0].end == _at(2)
    assert slots[1].start == _at(3) and slots[1].end == _at(8)


def test_overlapping_busy_intervals_are_merged():
    busy = [BusyInterval(_at(1), _at(3)), BusyInterval(_at(2), _at(4))]
    slots = find_free_slots(_at(0), _at(8), busy)
    assert len(slots) == 2
    assert slots[0].end == _at(1)
    assert slots[1].start == _at(4)


def test_busy_interval_outside_window_ignored():
    busy = [BusyInterval(_at(-5), _at(-4))]
    slots = find_free_slots(_at(0), _at(8), busy)
    assert len(slots) == 1
    assert slots[0].duration_seconds == 8 * 3600


def test_busy_interval_clipped_to_window_edges():
    busy = [BusyInterval(_at(-1), _at(1))]
    slots = find_free_slots(_at(0), _at(8), busy)
    assert len(slots) == 1
    assert slots[0].start == _at(1)


def test_min_duration_filters_short_slots():
    busy = [BusyInterval(_at(1), _at(1.9)), BusyInterval(_at(2), _at(8))]
    slots = find_free_slots(_at(0), _at(8), busy, min_duration_seconds=3600)
    # slot between 1.9 and 2 is only 6 minutes -> filtered out; slot 0-1 (1h) kept
    assert len(slots) == 1
    assert slots[0].start == _at(0) and slots[0].end == _at(1)


def test_invalid_window_returns_empty():
    assert find_free_slots(_at(5), _at(5), []) == []
    assert find_free_slots(_at(5), _at(4), []) == []
