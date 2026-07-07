from __future__ import annotations

import socket
from uuid import uuid4

from sqlalchemy.orm import Session

from court_hrms.models.audit_event import AuditEvent
from court_hrms.repositories.audit_repository import AuditRepository
from court_hrms.utils.audit_utils import calculate_entry_hash, canonical_json
from court_hrms.utils.time_utils import utc_now


APPLICATION_VERSION = "0.2.0"


class AuditService:
    def __init__(self, session: Session):
        self.repository = AuditRepository(session)

    def record_event(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: str | int | None = None,
        record_reference: str | None = None,
        user: dict | None = None,
        before: dict | None = None,
        after: dict | None = None,
        reason: str | None = None,
    ) -> AuditEvent:
        latest = self.repository.latest()
        previous_hash = latest.entry_hash if latest else ""
        timestamp = utc_now()
        event_uuid = str(uuid4())
        user_id = user.get("id") if user else None
        username = user.get("username") if user else None
        before_json = canonical_json(before) if before is not None else None
        after_json = canonical_json(after) if after is not None else None

        hash_payload = {
            "event_uuid": event_uuid,
            "timestamp_utc": timestamp,
            "user_id": user_id,
            "username_snapshot": username,
            "action": action,
            "entity_type": entity_type,
            "entity_id": None if entity_id is None else str(entity_id),
            "record_reference": record_reference,
            "before_json": before_json,
            "after_json": after_json,
            "reason": reason,
            "machine_name": socket.gethostname(),
            "application_version": APPLICATION_VERSION,
            "previous_hash": previous_hash,
        }
        entry_hash = calculate_entry_hash(hash_payload)

        event = AuditEvent(
            event_uuid=event_uuid,
            timestamp_utc=timestamp,
            user_id=user_id,
            username_snapshot=username,
            action=action,
            entity_type=entity_type,
            entity_id=None if entity_id is None else str(entity_id),
            record_reference=record_reference,
            before_json=before_json,
            after_json=after_json,
            reason=reason,
            machine_name=hash_payload["machine_name"],
            application_version=APPLICATION_VERSION,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
        )
        return self.repository.add(event)

    def verify_hash_chain(self) -> bool:
        previous_hash = ""
        for event in self.repository.list_all():
            if event.previous_hash != previous_hash:
                return False
            payload = {
                "event_uuid": event.event_uuid,
                "timestamp_utc": event.timestamp_utc,
                "user_id": event.user_id,
                "username_snapshot": event.username_snapshot,
                "action": event.action,
                "entity_type": event.entity_type,
                "entity_id": event.entity_id,
                "record_reference": event.record_reference,
                "before_json": event.before_json,
                "after_json": event.after_json,
                "reason": event.reason,
                "machine_name": event.machine_name,
                "application_version": event.application_version,
                "previous_hash": event.previous_hash,
            }
            if calculate_entry_hash(payload) != event.entry_hash:
                return False
            previous_hash = event.entry_hash
        return True
