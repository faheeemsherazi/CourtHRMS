from __future__ import annotations

from datetime import UTC, datetime

from court_hrms.utils.datetime_utils import (
    format_pakistan_datetime,
    to_pakistan_time,
)


def test_utc_timestamp_converts_to_pakistan_standard_time() -> None:
    utc_timestamp = datetime(2026, 7, 5, 20, 30, tzinfo=UTC)

    pakistan_time = to_pakistan_time(utc_timestamp)

    assert pakistan_time.hour == 1
    assert pakistan_time.day == 6
    assert format_pakistan_datetime(utc_timestamp) == "06-07-2026 01:30 AM"
