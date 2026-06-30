from __future__ import annotations

from court_hrms.database.db import SessionLocal, session_scope
from court_hrms.repositories.staff_repository import StaffRepository
from court_hrms.services.posting_service import PostingService
from court_hrms.services.service_record_service import ServiceRecordService
from court_hrms.utils.validators import ValidationError


class PostingController:
    def find_staff(self, personal_number: str) -> tuple[bool, str, dict | None, dict | None, list[dict]]:
        with session_scope() as session:
            staff = StaffRepository(session).get_by_personal_number((personal_number or "").strip())
            if staff is None:
                return False, "No staff profile found for this personal number.", None, None, []

            service = PostingService(session)
            current = service.get_current_posting(staff.id)
            history = service.history_for_staff(staff.id)
            service_record = ServiceRecordService(session).latest_for_staff(staff.id)
            staff_data = staff.to_dict()
            staff_data["has_service_record"] = service_record is not None

            return (
                True,
                "Staff profile found.",
                staff_data,
                current.to_dict() if current else None,
                [posting.to_dict() for posting in history],
            )

    def add_first_posting(self, data: dict) -> tuple[bool, str, dict | None]:
        try:
            with session_scope() as session:
                posting = PostingService(session).add_first_posting(data)
                return True, "First posting saved successfully.", posting.to_dict()
        except ValidationError as exc:
            return False, str(exc), None

    def execute_transfer(self, data: dict) -> tuple[bool, str, dict | None]:
        session = SessionLocal()
        try:
            posting = PostingService(session).execute_transfer(data)
            return True, "Transfer successful; posting history updated.", posting.to_dict()
        except ValidationError as exc:
            session.rollback()
            return False, str(exc), None
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def count_current_postings(self) -> int:
        with session_scope() as session:
            return PostingService(session).count_current_postings()
