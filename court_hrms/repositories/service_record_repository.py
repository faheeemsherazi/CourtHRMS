from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from court_hrms.models.service_record import ServiceRecord


class ServiceRecordRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, record: ServiceRecord) -> ServiceRecord:
        self.session.add(record)
        self.session.flush()
        return record

    def get_by_id(self, record_id: int) -> ServiceRecord | None:
        return self.session.get(ServiceRecord, record_id)

    def latest_for_staff(self, staff_id: int) -> ServiceRecord | None:
        stmt = (
            select(ServiceRecord)
            .where(ServiceRecord.staff_id == staff_id)
            .order_by(ServiceRecord.id.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_for_staff(self, staff_id: int) -> list[ServiceRecord]:
        stmt = (
            select(ServiceRecord)
            .where(ServiceRecord.staff_id == staff_id)
            .order_by(ServiceRecord.date_first_appointment.desc(), ServiceRecord.id.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def list_all(self) -> list[ServiceRecord]:
        stmt = (
            select(ServiceRecord)
            .options(joinedload(ServiceRecord.staff))
            .order_by(ServiceRecord.updated_at.desc(), ServiceRecord.id.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def count(self) -> int:
        stmt = select(func.count(ServiceRecord.id))
        return int(self.session.execute(stmt).scalar_one())

