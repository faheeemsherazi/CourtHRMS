from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from court_hrms.database.db import Base
from court_hrms.utils.time_utils import utc_now


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True)
    event_uuid = Column(String, unique=True, nullable=False, index=True)
    timestamp_utc = Column(DateTime, default=utc_now, nullable=False, index=True)
    user_id = Column(
        Integer,
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    username_snapshot = Column(String)
    action = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False, index=True)
    entity_id = Column(String, index=True)
    record_reference = Column(String, index=True)
    before_json = Column(Text)
    after_json = Column(Text)
    reason = Column(Text)
    machine_name = Column(String)
    application_version = Column(String)
    previous_hash = Column(String)
    entry_hash = Column(String, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_uuid": self.event_uuid,
            "timestamp_utc": self.timestamp_utc,
            "user_id": self.user_id,
            "username_snapshot": self.username_snapshot,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "record_reference": self.record_reference,
            "before_json": self.before_json,
            "after_json": self.after_json,
            "reason": self.reason,
            "machine_name": self.machine_name,
            "application_version": self.application_version,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
        }
