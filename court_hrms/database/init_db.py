from __future__ import annotations

import bcrypt

from court_hrms.database.db import Base, SessionLocal, engine
from court_hrms.models.admin import Admin
from court_hrms.models.posting_transfer import PostingTransfer
from court_hrms.models.service_record import ServiceRecord
from court_hrms.models.staff_profile import StaffProfile


DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"


def initialize_database() -> None:
    """Create all tables and seed the default administrator if missing."""
    # Model imports above register the table mappings with SQLAlchemy metadata.
    _ = (Admin, StaffProfile, ServiceRecord, PostingTransfer)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        existing_admin = (
            session.query(Admin)
            .filter(Admin.username == DEFAULT_ADMIN_USERNAME)
            .one_or_none()
        )
        if existing_admin is None:
            password_hash = bcrypt.hashpw(
                DEFAULT_ADMIN_PASSWORD.encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8")
            session.add(
                Admin(
                    username=DEFAULT_ADMIN_USERNAME,
                    password_hash=password_hash,
                    full_name="System Administrator",
                )
            )
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
