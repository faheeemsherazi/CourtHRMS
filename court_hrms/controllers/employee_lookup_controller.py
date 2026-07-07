from __future__ import annotations

from court_hrms.database.db import session_scope
from court_hrms.services.employee_lookup_service import EmployeeLookupService
from court_hrms.utils.exceptions import StaffNotFoundError
from court_hrms.utils.validators import ValidationError


class EmployeeLookupController:
    def by_staff_id(self, staff_id: int) -> tuple[bool, str, dict | None]:
        try:
            with session_scope() as session:
                data = EmployeeLookupService(session).by_staff_id(staff_id)
            return True, "Employee record found.", data
        except (StaffNotFoundError, ValidationError) as exc:
            return False, str(exc), None

    def by_personal_number(self, personal_number: str) -> tuple[bool, str, dict | None]:
        try:
            with session_scope() as session:
                data = EmployeeLookupService(session).by_personal_number(
                    personal_number
                )
            return True, "Employee record found.", data
        except (StaffNotFoundError, ValidationError) as exc:
            return False, str(exc), None
