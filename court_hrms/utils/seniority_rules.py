from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class SeniorityCandidate:
    staff_id: int
    personal_number: str
    full_name: str
    father_name: str
    designation: str
    bps: int | None
    date_first_appointment: date | None
    date_current_promotion: date | None
    selection_merit_number: int | None
    date_of_birth: date | None
    current_posting: str | None


@dataclass(frozen=True)
class SeniorityExclusion:
    personal_number: str
    full_name: str
    designation: str
    missing_field: str


@dataclass(frozen=True)
class SeniorityRankRow:
    rank: int
    personal_number: str
    full_name: str
    father_name: str
    designation: str
    bps: int | None
    date_first_appointment: date | None
    date_current_promotion: date | None
    selection_merit_number: int | None
    date_of_birth: date | None
    current_posting: str | None

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "personal_number": self.personal_number,
            "full_name": self.full_name,
            "father_name": self.father_name,
            "designation": self.designation,
            "bps": self.bps,
            "date_first_appointment": self.date_first_appointment,
            "date_current_promotion": self.date_current_promotion,
            "selection_merit_number": self.selection_merit_number,
            "date_of_birth": self.date_of_birth,
            "current_posting": self.current_posting,
        }


@dataclass(frozen=True)
class SeniorityResult:
    designation: str
    generated_at: datetime
    ranked: list[SeniorityRankRow]
    excluded: list[SeniorityExclusion]

    def to_dict(self) -> dict:
        return {
            "designation": self.designation,
            "generated_at": self.generated_at,
            "ranked": [row.to_dict() for row in self.ranked],
            "excluded": [
                {
                    "personal_number": exclusion.personal_number,
                    "full_name": exclusion.full_name,
                    "designation": exclusion.designation,
                    "missing_field": exclusion.missing_field,
                }
                for exclusion in self.excluded
            ],
            "ranked_count": len(self.ranked),
            "excluded_count": len(self.excluded),
        }


def seniority_sort_key(candidate: SeniorityCandidate) -> tuple:
    return (
        candidate.date_first_appointment or date.max,
        candidate.date_current_promotion or date.max,
        (
            candidate.selection_merit_number
            if candidate.selection_merit_number is not None
            else 10**9
        ),
        candidate.date_of_birth or date.max,
        candidate.personal_number,
    )


def rank_seniority_candidates(
    designation: str,
    candidates: list[SeniorityCandidate],
    generated_at: datetime,
) -> SeniorityResult:
    eligible: list[SeniorityCandidate] = []
    excluded: list[SeniorityExclusion] = []

    for candidate in candidates:
        if candidate.date_first_appointment is None:
            excluded.append(
                SeniorityExclusion(
                    personal_number=candidate.personal_number,
                    full_name=candidate.full_name,
                    designation=candidate.designation,
                    missing_field="Date of First Appointment",
                )
            )
            continue
        eligible.append(candidate)

    ranked = [
        SeniorityRankRow(
            rank=index,
            personal_number=candidate.personal_number,
            full_name=candidate.full_name,
            father_name=candidate.father_name,
            designation=candidate.designation,
            bps=candidate.bps,
            date_first_appointment=candidate.date_first_appointment,
            date_current_promotion=candidate.date_current_promotion,
            selection_merit_number=candidate.selection_merit_number,
            date_of_birth=candidate.date_of_birth,
            current_posting=candidate.current_posting,
        )
        for index, candidate in enumerate(
            sorted(eligible, key=seniority_sort_key), start=1
        )
    ]

    return SeniorityResult(
        designation=designation,
        generated_at=generated_at,
        ranked=ranked,
        excluded=excluded,
    )


SENIORITY_POLICY_SUMMARY = (
    "Official order: designation match, Active employees only, first appointment date "
    "ascending, current promotion date ascending with missing values last, selection "
    "merit number ascending with missing values last, date of birth ascending, then "
    "personal number ascending."
)
