from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from court_hrms.models.posting_transfer import PostingTransfer
from court_hrms.models.service_record import ServiceRecord
from court_hrms.models.staff_profile import StaffProfile
from court_hrms.utils.seniority_rules import SeniorityCandidate


class SeniorityRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_designations(self) -> list[str]:
        stmt = (
            select(ServiceRecord.designation)
            .where(ServiceRecord.designation.is_not(None))
            .distinct()
            .order_by(ServiceRecord.designation.asc())
        )
        return [
            designation for designation in self.session.execute(stmt).scalars().all()
        ]

    def list_active_candidates(self, designation: str) -> list[SeniorityCandidate]:
        latest_service = (
            select(
                ServiceRecord.staff_id.label("staff_id"),
                func.max(ServiceRecord.id).label("service_record_id"),
            )
            .group_by(ServiceRecord.staff_id)
            .subquery()
        )
        current_posting = (
            select(
                PostingTransfer.staff_id.label("staff_id"),
                func.max(PostingTransfer.id).label("posting_id"),
            )
            .where(PostingTransfer.is_current.is_(True))
            .group_by(PostingTransfer.staff_id)
            .subquery()
        )

        stmt = (
            select(
                StaffProfile.id,
                StaffProfile.personal_number,
                StaffProfile.full_name,
                StaffProfile.father_name,
                StaffProfile.date_of_birth,
                ServiceRecord.designation,
                ServiceRecord.bps,
                ServiceRecord.date_first_appointment,
                ServiceRecord.date_current_promotion,
                ServiceRecord.selection_merit_number,
                PostingTransfer.station_name,
            )
            .join(latest_service, latest_service.c.staff_id == StaffProfile.id)
            .join(ServiceRecord, ServiceRecord.id == latest_service.c.service_record_id)
            .outerjoin(current_posting, current_posting.c.staff_id == StaffProfile.id)
            .outerjoin(
                PostingTransfer, PostingTransfer.id == current_posting.c.posting_id
            )
            .where(
                ServiceRecord.designation == designation,
                ServiceRecord.employment_status == "Active",
            )
            .order_by(StaffProfile.personal_number.asc())
        )

        candidates: list[SeniorityCandidate] = []
        for row in self.session.execute(stmt).all():
            candidates.append(
                SeniorityCandidate(
                    staff_id=row.id,
                    personal_number=row.personal_number,
                    full_name=row.full_name,
                    father_name=row.father_name,
                    designation=row.designation,
                    bps=row.bps,
                    date_first_appointment=row.date_first_appointment,
                    date_current_promotion=row.date_current_promotion,
                    selection_merit_number=row.selection_merit_number,
                    date_of_birth=row.date_of_birth,
                    current_posting=row.station_name,
                )
            )
        return candidates
