from __future__ import annotations

from sqlalchemy.orm import Session

from court_hrms.repositories.seniority_repository import SeniorityRepository
from court_hrms.utils.app_logger import get_logger
from court_hrms.utils.seniority_rules import (
    SeniorityResult,
    rank_seniority_candidates,
)
from court_hrms.utils.time_utils import utc_now
from court_hrms.utils.validators import ValidationError, clean_text


class SeniorityService:
    def __init__(self, session: Session):
        self.repository = SeniorityRepository(session)
        self.logger = get_logger()

    def list_designations(self) -> list[str]:
        return self.repository.list_designations()

    def generate_seniority_list(self, designation: str) -> SeniorityResult:
        designation = clean_text(designation)
        if not designation:
            raise ValidationError("Designation is required.")

        candidates = self.repository.list_active_candidates(designation)
        result = rank_seniority_candidates(
            designation=designation,
            candidates=candidates,
            generated_at=utc_now(),
        )
        self.logger.info(
            "Seniority list generated; designation=%s ranked=%s excluded=%s",
            designation,
            len(result.ranked),
            len(result.excluded),
        )
        return result
