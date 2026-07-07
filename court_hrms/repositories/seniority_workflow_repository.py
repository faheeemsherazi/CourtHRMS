from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from court_hrms.models.seniority_workflow import (
    SeniorityList,
    SeniorityListEntry,
    SeniorityObjection,
)


class SeniorityWorkflowRepository:
    def __init__(self, session: Session):
        self.session = session

    def next_version(self, designation: str, list_year: int) -> int:
        stmt = select(func.max(SeniorityList.version_number)).where(
            SeniorityList.designation == designation,
            SeniorityList.list_year == list_year,
        )
        current = self.session.execute(stmt).scalar_one_or_none()
        return int(current or 0) + 1

    def add_list(self, seniority_list: SeniorityList) -> SeniorityList:
        self.session.add(seniority_list)
        self.session.flush()
        return seniority_list

    def add_entry(self, entry: SeniorityListEntry) -> SeniorityListEntry:
        self.session.add(entry)
        self.session.flush()
        return entry

    def get_list(self, seniority_list_id: int) -> SeniorityList | None:
        stmt = (
            select(SeniorityList)
            .options(selectinload(SeniorityList.entries))
            .where(SeniorityList.id == seniority_list_id)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_entries(self, seniority_list_id: int) -> list[SeniorityListEntry]:
        stmt = (
            select(SeniorityListEntry)
            .where(SeniorityListEntry.seniority_list_id == seniority_list_id)
            .order_by(SeniorityListEntry.rank.asc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def add_objection(self, objection: SeniorityObjection) -> SeniorityObjection:
        self.session.add(objection)
        self.session.flush()
        return objection
