from __future__ import annotations

import bcrypt

from court_hrms.database.db import Base, SessionLocal, engine
from court_hrms.database.migrations import apply_schema_upgrades
from court_hrms.models import (
    Admin,
    AnnualLeaveAccount,
    LeaveRecord,
    PostingTransfer,
    ServiceRecord,
    StaffProfile,
)
from court_hrms.utils.app_logger import get_logger


DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"


def initialize_database() -> None:
    """Create all tables and seed the default administrator if missing."""
    # Model imports above register the table mappings with SQLAlchemy metadata.
    _ = (
        Admin,
        StaffProfile,
        ServiceRecord,
        PostingTransfer,
        AnnualLeaveAccount,
        LeaveRecord,
    )
    apply_schema_upgrades()
    Base.metadata.create_all(bind=engine)

    logger = get_logger()
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
            logger.info("Default administrator account created")
    except Exception:
        session.rollback()
        logger.exception("Database initialization failed")
        raise
    finally:
        session.close()
