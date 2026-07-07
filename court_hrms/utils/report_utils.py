from __future__ import annotations

import re
from datetime import date, datetime
from html import escape
from pathlib import Path

from court_hrms.utils.datetime_utils import format_pakistan_datetime


FILENAME_SAFE_RE = re.compile(r"[^A-Za-z0-9._-]+")


def safe_text(value) -> str:
    if value is None or value == "":
        return "—"
    return escape(str(value))


def safe_optional_text(value) -> str:
    if value is None:
        return ""
    return escape(str(value))


def report_date(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, datetime):
        return format_pakistan_datetime(value, empty="—")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return escape(str(value))


def sanitize_filename(value: str) -> str:
    cleaned = FILENAME_SAFE_RE.sub("_", value.strip())
    cleaned = cleaned.strip("._")
    return cleaned or "report"


def ensure_pdf_suffix(path: str | Path) -> Path:
    output = Path(path)
    if output.suffix.lower() != ".pdf":
        output = output.with_suffix(".pdf")
    return output
