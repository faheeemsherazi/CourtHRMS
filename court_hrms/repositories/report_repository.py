from __future__ import annotations

from sqlalchemy.orm import Session

from court_hrms.repositories.leave_repository import LeaveRepository
from court_hrms.repositories.posting_repository import PostingRepository
from court_hrms.repositories.service_record_repository import ServiceRecordRepository
from court_hrms.repositories.staff_repository import StaffRepository


class ReportRepository:
    def __init__(self, session: Session):
        self.staff_repository = StaffRepository(session)
        self.service_record_repository = ServiceRecordRepository(session)
        self.posting_repository = PostingRepository(session)
        self.leave_repository = LeaveRepository(session)

    def get_staff_by_personal_number(self, personal_number: str):
        return self.staff_repository.get_by_personal_number(personal_number)

    def latest_service_record(self, staff_id: int):
        return self.service_record_repository.latest_for_staff(staff_id)

    def posting_history(self, staff_id: int):
        return self.posting_repository.history_for_staff(staff_id)

    def leave_accounts(self, staff_id: int):
        return self.leave_repository.list_accounts_for_staff(staff_id)

    def leave_history(self, staff_id: int, leave_year: int | None = None):
        return self.leave_repository.list_records_for_staff(staff_id, leave_year)
