from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from court_hrms.models.staff_profile import StaffProfile


class StaffRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, staff: StaffProfile) -> StaffProfile:
        self.session.add(staff)
        self.session.flush()
        return staff

    def get_by_id(self, staff_id: int) -> StaffProfile | None:
        return self.session.get(StaffProfile, staff_id)

    def get_by_personal_number(self, personal_number: str) -> StaffProfile | None:
        stmt = select(StaffProfile).where(
            StaffProfile.personal_number == personal_number
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_cnic(self, cnic: str) -> StaffProfile | None:
        stmt = select(StaffProfile).where(StaffProfile.cnic == cnic)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[StaffProfile]:
        stmt = select(StaffProfile).order_by(StaffProfile.full_name.asc())
        return list(self.session.execute(stmt).scalars().all())

    def count(self) -> int:
        stmt = select(func.count(StaffProfile.id))
        return int(self.session.execute(stmt).scalar_one())
