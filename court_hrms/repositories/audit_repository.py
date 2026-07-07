from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from court_hrms.models.audit_event import AuditEvent


class AuditRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, event: AuditEvent) -> AuditEvent:
        self.session.add(event)
        self.session.flush()
        return event

    def latest(self) -> AuditEvent | None:
        stmt = select(AuditEvent).order_by(AuditEvent.id.desc()).limit(1)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[AuditEvent]:
        stmt = select(AuditEvent).order_by(AuditEvent.id.asc())
        return list(self.session.execute(stmt).scalars().all())
