from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from court_hrms.models.seniority_workflow import (
    SeniorityList,
    SeniorityListEntry,
    SeniorityObjection,
)
from court_hrms.repositories.seniority_workflow_repository import (
    SeniorityWorkflowRepository,
)
from court_hrms.services.seniority_service import SeniorityService
from court_hrms.utils.exceptions import SeniorityDataError
from court_hrms.utils.master_data import (
    SENIORITY_LIST_STATUSES,
    SENIORITY_LIST_TYPES,
    SENIORITY_OBJECTION_STATUSES,
)
from court_hrms.utils.seniority_rules import SENIORITY_POLICY_SUMMARY
from court_hrms.utils.time_utils import utc_now
from court_hrms.utils.validators import ValidationError, clean_text


class SeniorityWorkflowService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = SeniorityWorkflowRepository(session)
        self.seniority_service = SeniorityService(session)

    def create_snapshot(
        self,
        *,
        designation: str,
        list_year: int,
        list_type: str = "Draft",
        title: str | None = None,
        cutoff_date: date | None = None,
        generated_by: int | None = None,
        remarks: str | None = None,
    ) -> SeniorityList:
        designation = clean_text(designation)
        if not designation:
            raise ValidationError("Designation is required.")
        if list_type not in SENIORITY_LIST_TYPES:
            raise ValidationError("Seniority list type is not valid.")
        if list_year < 1900 or list_year > 9999:
            raise ValidationError("Seniority list year must be a four-digit year.")

        result = self.seniority_service.generate_seniority_list(designation)
        if not result.ranked:
            raise SeniorityDataError(
                "No eligible staff records were found for the selected designation."
            )

        version = self.repository.next_version(designation, list_year)
        seniority_list = SeniorityList(
            title=title or f"{list_type} Seniority List - {designation} - {list_year}",
            designation=designation,
            list_year=list_year,
            version_number=version,
            list_type=list_type,
            status="Generated",
            cutoff_date=cutoff_date,
            generated_at=utc_now(),
            generated_by=generated_by,
            remarks=remarks,
        )
        self.repository.add_list(seniority_list)

        for row in result.ranked:
            self.repository.add_entry(
                SeniorityListEntry(
                    seniority_list_id=seniority_list.id,
                    staff_id=row.staff_id,
                    rank=row.rank,
                    personal_number=row.personal_number,
                    full_name=row.full_name,
                    father_name=row.father_name,
                    qualification=row.qualification,
                    designation=row.designation,
                    bps=row.bps,
                    date_of_birth=row.date_of_birth,
                    first_government_entry=row.first_government_entry,
                    first_judiciary_entry=row.first_judiciary_entry,
                    current_post_date=row.current_post_date,
                    promotion_date=row.date_current_promotion,
                    retirement_date=row.retirement_date,
                    current_posting=row.current_posting,
                    ranking_basis=SENIORITY_POLICY_SUMMARY,
                    remarks=row.remarks,
                )
            )
        self.session.flush()
        return seniority_list

    def finalize_list(
        self,
        seniority_list_id: int,
        *,
        finalized_by: int | None = None,
        approval_order_number: str | None = None,
        approval_order_date: date | None = None,
    ) -> SeniorityList:
        seniority_list = self.repository.get_list(seniority_list_id)
        if seniority_list is None:
            raise SeniorityDataError("Seniority list was not found.")
        if seniority_list.status == "Finalized":
            raise SeniorityDataError(
                "Finalized seniority lists cannot be modified silently."
            )

        seniority_list.status = "Finalized"
        seniority_list.list_type = (
            "Final" if seniority_list.list_type != "Revised Final" else "Revised Final"
        )
        seniority_list.finalized_date = utc_now().date()
        seniority_list.finalized_by = finalized_by
        seniority_list.approval_order_number = clean_text(approval_order_number)
        seniority_list.approval_order_date = approval_order_date
        self.session.flush()
        return seniority_list

    def create_objection(
        self,
        *,
        seniority_list_id: int,
        objection_number: str,
        staff_id: int,
        submitted_date: date,
        subject: str,
        details: str,
        status: str = "Received",
    ) -> SeniorityObjection:
        seniority_list = self.repository.get_list(seniority_list_id)
        if seniority_list is None:
            raise SeniorityDataError("Seniority list was not found.")
        if seniority_list.status == "Finalized":
            raise SeniorityDataError(
                "Finalized seniority lists cannot accept new objections."
            )
        if status not in SENIORITY_OBJECTION_STATUSES:
            raise ValidationError("Seniority objection status is not valid.")

        objection_number = clean_text(objection_number)
        subject = clean_text(subject)
        details = clean_text(details)
        if not objection_number or not subject or not details:
            raise ValidationError("Objection number, subject and details are required.")

        objection = SeniorityObjection(
            objection_number=objection_number,
            seniority_list_id=seniority_list_id,
            staff_id=staff_id,
            submitted_date=submitted_date,
            subject=subject,
            details=details,
            status=status,
        )
        return self.repository.add_objection(objection)

    @staticmethod
    def valid_statuses() -> tuple[str, ...]:
        return SENIORITY_LIST_STATUSES
