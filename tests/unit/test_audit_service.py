from __future__ import annotations

import unittest

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from court_hrms.database.db import Base
from court_hrms.models import Admin, AuditEvent
from court_hrms.services.audit_service import AuditService


class AuditServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:", future=True)

        @event.listens_for(self.engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        Base.metadata.create_all(self.engine)
        session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            future=True,
        )
        self.session = session_factory()
        self.session.add(Admin(id=1, username="admin", password_hash="hash"))
        self.session.flush()
        self.service = AuditService(self.session)

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_audit_hash_chain_verifies_and_redacts_passwords(self) -> None:
        self.service.record_event(
            action="CREATE",
            entity_type="StaffProfile",
            entity_id=1,
            record_reference="PN-001",
            user={"id": 1, "username": "admin"},
            after={"personal_number": "PN-001", "password": "plain"},
        )
        self.service.record_event(
            action="UPDATE",
            entity_type="StaffProfile",
            entity_id=1,
            record_reference="PN-001",
            user={"id": 1, "username": "admin"},
            before={"full_name": "Old"},
            after={"full_name": "New"},
            reason="Correction",
        )
        self.session.commit()

        events = self.session.query(AuditEvent).order_by(AuditEvent.id.asc()).all()

        self.assertEqual(len(events), 2)
        self.assertIn("[REDACTED]", events[0].after_json)
        self.assertTrue(self.service.verify_hash_chain())

    def test_audit_hash_chain_detects_modified_entry(self) -> None:
        event = self.service.record_event(
            action="CREATE",
            entity_type="StaffProfile",
            entity_id=1,
            record_reference="PN-001",
        )
        self.session.commit()

        with self.engine.begin() as connection:
            connection.execute(
                text("UPDATE audit_events SET action='UPDATE' WHERE id=:id"),
                {"id": event.id},
            )

        self.session.expire_all()

        self.assertFalse(self.service.verify_hash_chain())


if __name__ == "__main__":
    unittest.main()
