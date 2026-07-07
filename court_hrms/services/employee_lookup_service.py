from __future__ import annotations

from sqlalchemy.orm import Session

from court_hrms.repositories.posting_repository import PostingRepository
from court_hrms.repositories.service_record_repository import ServiceRecordRepository
from court_hrms.repositories.staff_repository import StaffRepository
from court_hrms.utils.exceptions import StaffNotFoundError


def mask_cnic(value: str | None) -> str:
    if not value:
        return ""
    digits = str(value)
    if len(digits) <= 4:
        return "*" * len(digits)
    return f"{'*' * (len(digits) - 4)}{digits[-4:]}"


class EmployeeLookupService:
    def __init__(self, session: Session):
        self.staff_repository = StaffRepository(session)
        self.service_record_repository = ServiceRecordRepository(session)
        self.posting_repository = PostingRepository(session)

    def by_staff_id(self, staff_id: int) -> dict:
        staff = self.staff_repository.get_by_id(staff_id)
        if staff is None:
            raise StaffNotFoundError("No staff profile found for this employee.")
        return self._build_context(staff)

    def by_personal_number(self, personal_number: str) -> dict:
        personal_number = (personal_number or "").strip()
        if not personal_number:
            raise StaffNotFoundError("Personal number is required.")

        staff = self.staff_repository.get_by_personal_number(personal_number)
        if staff is None:
            raise StaffNotFoundError("No staff profile found for this personal number.")
        return self._build_context(staff)

    def _build_context(self, staff) -> dict:
        service = self.service_record_repository.latest_for_staff(staff.id)
        posting = self.posting_repository.get_current_for_staff(staff.id)

        return {
            "staff_id": staff.id,
            "personal_number": staff.personal_number,
            "full_name": staff.full_name,
            "father_name": staff.father_name,
            "cnic": staff.cnic,
            "cnic_masked": mask_cnic(staff.cnic),
            "date_of_birth": staff.date_of_birth,
            "date_of_retirement": staff.date_of_retirement,
            "mobile_number": staff.mobile_number,
            "domicile": staff.domicile,
            "district": staff.district,
            "designation": service.designation if service else "",
            "bps": service.bps if service else None,
            "employment_type": service.employment_type if service else "",
            "employment_status": service.employment_status if service else "",
            "date_first_appointment": (
                service.date_first_appointment if service else None
            ),
            "date_current_promotion": (
                service.date_current_promotion if service else None
            ),
            "current_posting": posting.station_name if posting else "",
        }
