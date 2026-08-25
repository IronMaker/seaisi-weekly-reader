from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


TAIPEI = ZoneInfo("Asia/Taipei")


@dataclass(frozen=True)
class WeeklyBoundary:
    start: datetime
    end: datetime


def previous_complete_cycle(now: datetime | None = None) -> WeeklyBoundary:
    """
    Return the previous fully completed SEAISI weekly cycle:
    Wednesday 00:00:00 through Tuesday 23:59:59.999999 Asia/Taipei.

    If called during Tuesday, the current Wed-Tue cycle is not yet complete,
    so the function returns the preceding cycle.
    """
    if now is None:
        now = datetime.now(TAIPEI)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=TAIPEI)
    else:
        now = now.astimezone(TAIPEI)

    # Python weekday: Monday=0 ... Tuesday=1 ... Wednesday=2
    days_since_wednesday = (now.weekday() - 2) % 7
    current_cycle_start = (now - timedelta(days=days_since_wednesday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    current_cycle_end = current_cycle_start + timedelta(days=7)

    if now >= current_cycle_end:
        completed_start = current_cycle_start
    else:
        completed_start = current_cycle_start - timedelta(days=7)

    completed_end = completed_start + timedelta(days=7) - timedelta(microseconds=1)

    return WeeklyBoundary(start=completed_start, end=completed_end)
