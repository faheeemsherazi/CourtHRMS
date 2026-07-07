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


@dataclass(frozen=True)
class PostingHistoryReport:
    staff: dict
    service_record: dict | None
    posting_history: list[dict]
    generated_at: datetime


@dataclass(frozen=True)
class TransferHistoryReport:
    staff: dict
    service_record: dict | None
    transfer_history: list[dict]
    generated_at: datetime


@dataclass(frozen=True)
class ServiceBookExtractReport:
    staff: dict
    service_records: list[dict]
    service_events: list[dict]
    posting_history: list[dict]
    generated_at: datetime


@dataclass(frozen=True)
class EmployeeDossierReport:
    profile: IndividualProfileReport
    service_book: ServiceBookExtractReport
    leave_history: list[dict]
    leave_ledger: list[dict]
    generated_at: datetime
