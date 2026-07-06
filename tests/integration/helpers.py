from __future__ import annotations

from datetime import date

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from court_hrms.database.db import Base
from court_hrms.models import Admin, ServiceRecord, StaffProfile


def create_test_session() -> tuple:
    engine = create_engine("sqlite:///:memory:", future=True)

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    return engine, session_factory()


def add_admin(session: Session) -> Admin:
    admin = Admin(username="admin", password_hash="hash", full_name="System Admin")
    session.add(admin)
    session.flush()
    return admin


def add_staff(
    session: Session,
    personal_number: str,
    full_name: str = "Muhammad Ali Khan",
    birth: date = date(1980, 1, 1),
) -> StaffProfile:
    staff = StaffProfile(
        personal_number=personal_number,
        full_name=full_name,
        father_name="Abdul Karim Khan",
        cnic=f"17301123{personal_number[-4:]}",
        date_of_birth=birth,
        district="Orakzai",
        mobile_number="03001234567",
        present_address="District Court Orakzai",
        permanent_address="District Orakzai",
    )
    session.add(staff)
    session.flush()
    return staff


def add_service_record(
    session: Session,
    staff_id: int,
    designation: str = "Junior Clerk",
    appointment: date = date(2010, 1, 1),
    status: str = "Active",
    merit: int | None = None,
) -> ServiceRecord:
    record = ServiceRecord(
        staff_id=staff_id,
        designation=designation,
        bps=9,
        employment_type="Permanent",
        employment_status=status,
        date_first_appointment=appointment,
        selection_merit_number=merit,
    )
    session.add(record)
    session.flush()
    return record
