from __future__ import annotations

from datetime import date, datetime


def today() -> date:
    return date.today()


def add_years(value: date, years: int) -> date:
    """Add calendar years, handling leap-day birthdays safely."""
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(month=2, day=28, year=value.year + years)


def calculate_age(birth_date: date, on_date: date | None = None) -> int:
    reference = on_date or today()
    years = reference.year - birth_date.year
    if (reference.month, reference.day) < (birth_date.month, birth_date.day):
        years -= 1
    return years


def calculate_retirement_date(birth_date: date) -> date:
    return add_years(birth_date, 60)


def coerce_date(value, field_name: str) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str) and value.strip():
        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError(
                f"{field_name} must be a valid date in YYYY-MM-DD format."
            ) from exc
    raise ValueError(f"{field_name} is required.")


def format_date(value: date | datetime | None) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        value = value.date()
    return value.strftime("%Y-%m-%d")
