from __future__ import annotations

import re
from datetime import date
from typing import Any

from court_hrms.utils.date_utils import calculate_age, coerce_date


EMAIL_RE = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
CNIC_RE = re.compile(r"^\d{13}$")
DIGITS_RE = re.compile(r"^\d+$")

EMPLOYMENT_TYPES = ("Permanent", "Contract", "Temporary")
EMPLOYMENT_STATUSES = ("Active", "Retired", "Suspended")

DESIGNATION_BPS_RANGES = {
    "Naib Qasid": (1, 5),
    "Junior Clerk": (7, 11),
    "Senior Clerk": (11, 14),
    "Stenographer": (14, 16),
    "Superintendent": (16, 18),
    "Civil Judge": (17, 19),
    "Additional District Judge": (20, 21),
    "District & Sessions Judge": (21, 22),
}


class ValidationError(Exception):
    """Raised by services when one or more business validations fail."""

    def __init__(self, messages: list[str] | str):
        if isinstance(messages, str):
            messages = [messages]
        self.messages = messages
        super().__init__("\n".join(messages))


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def require_text(data: dict, field: str, label: str, errors: list[str]) -> str | None:
    value = clean_text(data.get(field))
    if not value:
        errors.append(f"{label} is required.")
    return value


def optional_text(data: dict, field: str) -> str | None:
    return clean_text(data.get(field))


def validate_cnic(value: str | None, errors: list[str]) -> None:
    if not value:
        errors.append("CNIC is required.")
        return
    if not CNIC_RE.match(value):
        errors.append("CNIC must be exactly 13 digits without dashes.")


def validate_exact_digits(
    value: str | None,
    label: str,
    digits: int,
    errors: list[str],
    *,
    required: bool = False,
) -> None:
    if not value:
        if required:
            errors.append(f"{label} is required.")
        return
    if not DIGITS_RE.match(value) or len(value) != digits:
        errors.append(f"{label} must be exactly {digits} digits.")


def validate_digits_max_length(
    value: str | None,
    label: str,
    max_digits: int,
    errors: list[str],
    *,
    required: bool = False,
) -> None:
    if not value:
        if required:
            errors.append(f"{label} is required.")
        return
    if not DIGITS_RE.match(value):
        errors.append(f"{label} must contain digits only.")
        return
    if len(value) > max_digits:
        errors.append(f"{label} cannot be more than {max_digits} digits.")


def validate_minimum_length(
    value: str | None,
    label: str,
    min_characters: int,
    errors: list[str],
    *,
    required: bool = False,
) -> None:
    if not value:
        if required:
            errors.append(f"{label} is required.")
        return
    if len(value) < min_characters:
        errors.append(f"{label} must be at least {min_characters} characters.")


def validate_email(value: str | None, errors: list[str]) -> None:
    if value and not EMAIL_RE.match(value):
        errors.append("Email address is not valid.")


def validate_adult_birth_date(value, errors: list[str]) -> date | None:
    try:
        birth_date = coerce_date(value, "Date of birth")
    except ValueError as exc:
        errors.append(str(exc))
        return None

    if calculate_age(birth_date) < 18:
        errors.append("Date of birth must show the employee is at least 18 years old.")
    return birth_date


def validate_bps(value, errors: list[str]) -> int | None:
    try:
        bps = int(value)
    except (TypeError, ValueError):
        errors.append("BPS must be a number between 1 and 22.")
        return None

    if not 1 <= bps <= 22:
        errors.append("BPS must be between 1 and 22.")
    return bps


def validate_designation_bps(designation: str | None, bps: int | None, errors: list[str]) -> None:
    if not designation or bps is None:
        return
    bps_range = DESIGNATION_BPS_RANGES.get(designation)
    if bps_range is None:
        return

    min_bps, max_bps = bps_range
    if not min_bps <= bps <= max_bps:
        errors.append(
            f"{designation} is compatible with BPS {min_bps} to {max_bps} only."
        )


def validate_choice(value: str | None, allowed: tuple[str, ...], label: str, errors: list[str]) -> str | None:
    if not value:
        errors.append(f"{label} is required.")
        return None
    if value not in allowed:
        errors.append(f"{label} must be one of: {', '.join(allowed)}.")
        return None
    return value
