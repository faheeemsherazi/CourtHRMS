from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class IndividualProfileReport:
    staff: dict
    service_record: dict | None
    posting_history: list[dict]
    leave_summaries: list[dict]
    generated_at: datetime


@dataclass(frozen=True)
class LeaveHistoryReport:
    staff: dict
    service_record: dict | None
    selected_year: int | None
    summaries: list[dict]
    history: list[dict]
    generated_at: datetime


@dataclass(frozen=True)
class SeniorityListReport:
    designation: str
    generated_at: datetime
    ranked: list[dict]
    excluded: list[dict]
    policy_summary: str
