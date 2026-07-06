from __future__ import annotations

from sqlalchemy.orm import Session

from court_hrms.reporting.report_dtos import (
    IndividualProfileReport,
    LeaveHistoryReport,
    SeniorityListReport,
)
from court_hrms.repositories.report_repository import ReportRepository
from court_hrms.services.leave_service import LeaveService
from court_hrms.services.seniority_service import SeniorityService
from court_hrms.utils.exceptions import ReportDataNotFoundError
from court_hrms.utils.leave_rules import validate_leave_year
from court_hrms.utils.seniority_rules import SENIORITY_POLICY_SUMMARY
from court_hrms.utils.time_utils import utc_now


class ReportService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = ReportRepository(session)
        self.leave_service = LeaveService(session)
        self.seniority_service = SeniorityService(session)

    def individual_profile(self, personal_number: str) -> IndividualProfileReport:
        staff = self._require_staff(personal_number)
        service_record = self.repository.latest_service_record(staff.id)
        posting_history = self.repository.posting_history(staff.id)
        leave_summaries = [
            account.to_dict() for account in self.repository.leave_accounts(staff.id)
        ]

        return IndividualProfileReport(
            staff=staff.to_dict(),
            service_record=service_record.to_dict() if service_record else None,
            posting_history=[posting.to_dict() for posting in posting_history],
            leave_summaries=leave_summaries,
            generated_at=utc_now(),
        )

    def leave_history(
        self,
        personal_number: str,
        leave_year: int | None = None,
    ) -> LeaveHistoryReport:
        staff = self._require_staff(personal_number)
        service_record = self.repository.latest_service_record(staff.id)

        if leave_year is not None:
            leave_year = validate_leave_year(leave_year)
            summaries = [self.leave_service.get_account_summary(staff.id, leave_year)]
            history = self.leave_service.list_history(staff.id, leave_year)
        else:
            summaries = [
                account.to_dict()
                for account in self.repository.leave_accounts(staff.id)
            ]
            history = self.leave_service.list_history(staff.id)

        if not history:
            raise ReportDataNotFoundError(
                "No leave history records were found for the selected filters."
            )

        return LeaveHistoryReport(
            staff=staff.to_dict(),
            service_record=service_record.to_dict() if service_record else None,
            selected_year=leave_year,
            summaries=summaries,
            history=history,
            generated_at=utc_now(),
        )

    def seniority_list(self, designation: str) -> SeniorityListReport:
        result = self.seniority_service.generate_seniority_list(designation)
        if not result.ranked:
            raise ReportDataNotFoundError(
                "No eligible staff records were found for the selected designation."
            )

        data = result.to_dict()
        return SeniorityListReport(
            designation=result.designation,
            generated_at=result.generated_at,
            ranked=data["ranked"],
            excluded=data["excluded"],
            policy_summary=SENIORITY_POLICY_SUMMARY,
        )

    def _require_staff(self, personal_number: str):
        personal_number = (personal_number or "").strip()
        if not personal_number:
            raise ReportDataNotFoundError(
                "No records found for the supplied Personal Number."
            )

        staff = self.repository.get_staff_by_personal_number(personal_number)
        if staff is None:
            raise ReportDataNotFoundError(
                "No records found for the supplied Personal Number."
            )
        return staff
