from __future__ import annotations

from court_hrms.database.db import session_scope
from court_hrms.services.staff_service import StaffService
from court_hrms.utils.validators import ValidationError


class StaffController:
    def create_profile(self, data: dict) -> tuple[bool, str, dict | None]:
        try:
            with session_scope() as session:
                staff = StaffService(session).create_staff(data)
                return True, "Staff profile saved successfully.", staff.to_dict()
        except ValidationError as exc:
            return False, str(exc), None

    def update_profile(
        self, staff_id: int, data: dict
    ) -> tuple[bool, str, dict | None]:
        try:
            with session_scope() as session:
                staff = StaffService(session).update_staff(staff_id, data)
                return True, "Staff profile updated successfully.", staff.to_dict()
        except ValidationError as exc:
            return False, str(exc), None

    def search_by_personal_number(
        self, personal_number: str
    ) -> tuple[bool, str, dict | None]:
        with session_scope() as session:
            staff = StaffService(session).get_by_personal_number(personal_number)
            if staff is None:
                return False, "No staff profile found for this personal number.", None
            return True, "Staff profile found.", staff.to_dict()

    def list_profiles(self) -> list[dict]:
        with session_scope() as session:
            return [staff.to_dict() for staff in StaffService(session).list_staff()]

    def count_profiles(self) -> int:
        with session_scope() as session:
            return StaffService(session).count_staff()
