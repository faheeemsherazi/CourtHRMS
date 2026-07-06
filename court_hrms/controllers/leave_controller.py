from __future__ import annotations

from court_hrms.database.db import SessionLocal, session_scope
from court_hrms.services.leave_service import LeaveService
from court_hrms.utils.app_logger import get_logger
from court_hrms.utils.exceptions import DatabaseOperationError
from court_hrms.utils.leave_rules import validate_leave_dates
from court_hrms.utils.validators import ValidationError


class LeaveController:
    def __init__(self, admin: dict | None = None):
        self.admin = admin or {}
        self.logger = get_logger()

    def set_authenticated_admin(self, admin: dict | None) -> None:
        self.admin = admin or {}

    def clear_session(self) -> None:
        self.admin = {}

    def calculate_days(self, start_value, end_value) -> tuple[bool, str, int | None]:
        try:
            _start_date, _end_date, days = validate_leave_dates(start_value, end_value)
            return True, "", days
        except ValidationError as exc:
            return False, str(exc), None

    def find_staff(
        self, personal_number: str, leave_year: int
    ) -> tuple[bool, str, dict | None]:
        try:
            with session_scope() as session:
                context = LeaveService(session).find_staff_context(
                    personal_number, leave_year
                )
                return True, "Staff profile found.", context
        except ValidationError as exc:
            return False, str(exc), None

    def get_summary(
        self, staff_id: int, leave_year: int
    ) -> tuple[bool, str, dict | None]:
        try:
            with session_scope() as session:
                summary = LeaveService(session).get_account_summary(
                    staff_id, leave_year
                )
                return True, "Leave balance loaded.", summary
        except ValidationError as exc:
            return False, str(exc), None

    def list_history(
        self,
        staff_id: int,
        leave_year: int | None = None,
    ) -> tuple[bool, str, list[dict]]:
        try:
            with session_scope() as session:
                history = LeaveService(session).list_history(staff_id, leave_year)
                return True, "Leave history loaded.", history
        except ValidationError as exc:
            return False, str(exc), []

    def list_account_years(self, staff_id: int) -> list[int]:
        with session_scope() as session:
            return LeaveService(session).list_account_years(staff_id)

    def process_leave(self, data: dict) -> tuple[bool, str, dict | None]:
        payload = dict(data)
        payload["processed_by_admin_id"] = self.admin.get("id")
        session = SessionLocal()
        try:
            result = LeaveService(session).process_leave(payload)
            return True, result["message"], result
        except ValidationError as exc:
            session.rollback()
            return False, str(exc), None
        except DatabaseOperationError:
            session.rollback()
            return False, "Leave could not be recorded. Please try again.", None
        except Exception:
            session.rollback()
            self.logger.exception("Unexpected leave controller failure")
            return False, "Leave could not be recorded. Please try again.", None
        finally:
            session.close()
