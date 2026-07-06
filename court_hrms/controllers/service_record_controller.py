from __future__ import annotations

from court_hrms.database.db import session_scope
from court_hrms.repositories.staff_repository import StaffRepository
from court_hrms.services.service_record_service import ServiceRecordService
from court_hrms.utils.validators import ValidationError


class ServiceRecordController:
    def create_record(self, data: dict) -> tuple[bool, str, dict | None]:
        try:
            with session_scope() as session:
                service = ServiceRecordService(session)
                record = service.create_record(data)
                return (
                    True,
                    "Service record saved successfully.",
                    self._record_to_dict(record),
                )
        except ValidationError as exc:
            return False, str(exc), None

    def update_record(
        self, record_id: int, data: dict
    ) -> tuple[bool, str, dict | None]:
        try:
            with session_scope() as session:
                service = ServiceRecordService(session)
                record = service.update_record(record_id, data)
                return (
                    True,
                    "Service record updated successfully.",
                    self._record_to_dict(record),
                )
        except ValidationError as exc:
            return False, str(exc), None

    def find_staff(
        self, personal_number: str
    ) -> tuple[bool, str, dict | None, dict | None]:
        with session_scope() as session:
            staff = StaffRepository(session).get_by_personal_number(
                (personal_number or "").strip()
            )
            if staff is None:
                return (
                    False,
                    "No staff profile found for this personal number.",
                    None,
                    None,
                )

            latest_record = ServiceRecordService(session).latest_for_staff(staff.id)
            return (
                True,
                "Staff profile found.",
                staff.to_dict(),
                self._record_to_dict(latest_record) if latest_record else None,
            )

    def list_records(self) -> list[dict]:
        with session_scope() as session:
            records = ServiceRecordService(session).list_records()
            return [self._record_to_dict(record) for record in records]

    def count_records(self) -> int:
        with session_scope() as session:
            return ServiceRecordService(session).count_records()

    @staticmethod
    def _record_to_dict(record) -> dict | None:
        if record is None:
            return None
        data = record.to_dict()
        staff = getattr(record, "staff", None)
        data["staff_personal_number"] = staff.personal_number if staff else ""
        data["staff_full_name"] = staff.full_name if staff else ""
        return data
