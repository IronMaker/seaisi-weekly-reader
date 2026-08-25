from datetime import datetime
from zoneinfo import ZoneInfo

from seaisi_weekly_reader.boundary import previous_complete_cycle


TZ = ZoneInfo("Asia/Taipei")


def test_tuesday_returns_previous_complete_cycle():
    now = datetime(2026, 8, 25, 13, 59, tzinfo=TZ)
    result = previous_complete_cycle(now)

    assert result.start.isoformat() == "2026-08-12T00:00:00+08:00"
    assert result.end.isoformat() == "2026-08-18T23:59:59.999999+08:00"


def test_wednesday_still_returns_previous_complete_cycle():
    now = datetime(2026, 8, 26, 9, 0, tzinfo=TZ)
    result = previous_complete_cycle(now)

    assert result.start.isoformat() == "2026-08-19T00:00:00+08:00"
    assert result.end.isoformat() == "2026-08-25T23:59:59.999999+08:00"
