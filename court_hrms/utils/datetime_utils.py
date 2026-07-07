from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo


PAKISTAN_TZ = ZoneInfo("Asia/Karachi")
DISPLAY_DATETIME_FORMAT = "%d-%m-%Y %I:%M %p"
DATE_SUFFIX_FORMAT = "%Y%m%d"


def ensure_utc_aware(value: datetime) -> datetime:
    """Treat stored naive values as UTC and return an aware UTC datetime."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def to_pakistan_time(value: datetime) -> datetime:
    return ensure_utc_aware(value).astimezone(PAKISTAN_TZ)


def format_pakistan_datetime(value: datetime | None, empty: str = "") -> str:
    if value is None:
        return empty
    return to_pakistan_time(value).strftime(DISPLAY_DATETIME_FORMAT)


def pakistan_date_suffix(value: datetime | None = None) -> str:
    value = value or datetime.now(UTC)
    return to_pakistan_time(value).strftime(DATE_SUFFIX_FORMAT)
