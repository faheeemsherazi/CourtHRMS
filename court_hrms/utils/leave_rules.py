from __future__ import annotations

from datetime import date

from court_hrms.utils.date_utils import coerce_date
from court_hrms.utils.exceptions import LeaveDateError


ANNUAL_LEAVE_ENTITLEMENT_DAYS = 25
MIN_LEAVE_YEAR = 1900
MAX_LEAVE_YEAR = 9999


def calculate_inclusive_leave_days(start_date: date, end_date: date) -> int:
    days = (end_date - start_date).days + 1
    if days <= 0:
        raise LeaveDateError("Requested leave days must be greater than zero.")
    return days


def validate_leave_year(value) -> int:
    try:
        leave_year = int(value)
    except (TypeError, ValueError) as exc:
        raise LeaveDateError("Leave year must be a four-digit year.") from exc

    if not MIN_LEAVE_YEAR <= leave_year <= MAX_LEAVE_YEAR:
        raise LeaveDateError("Leave year must be a four-digit year.")
    return leave_year


def validate_leave_dates(start_value, end_value) -> tuple[date, date, int]:
    try:
        start_date = coerce_date(start_value, "Start date")
        end_date = coerce_date(end_value, "End date")
    except ValueError as exc:
        raise LeaveDateError(str(exc)) from exc

    if end_date < start_date:
        raise LeaveDateError("End date cannot be before start date.")
    if start_date.year != end_date.year:
        raise LeaveDateError(
            "A leave request cannot cross calendar years. Record each year separately."
        )

    return start_date, end_date, calculate_inclusive_leave_days(start_date, end_date)
