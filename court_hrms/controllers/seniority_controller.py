from __future__ import annotations

from court_hrms.database.db import session_scope
from court_hrms.services.seniority_service import SeniorityService
from court_hrms.utils.app_logger import get_logger
from court_hrms.utils.validators import ValidationError


class SeniorityController:
    def __init__(self):
        self.logger = get_logger()

    def list_designations(self) -> list[str]:
        with session_scope() as session:
            return SeniorityService(session).list_designations()

    def generate_list(self, designation: str) -> tuple[bool, str, dict | None]:
        try:
            with session_scope() as session:
                result = SeniorityService(session).generate_seniority_list(designation)
                return True, "Seniority list generated.", result.to_dict()
        except ValidationError as exc:
            return False, str(exc), None
        except Exception:
            self.logger.exception("Unexpected seniority controller failure")
            return False, "Seniority list could not be generated.", None
