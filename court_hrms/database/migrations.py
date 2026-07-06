from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from sqlalchemy import inspect, text

from court_hrms.database.db import Base, DATABASE_PATH, engine
from court_hrms.models.annual_leave_account import AnnualLeaveAccount
from court_hrms.models.leave_record import LeaveRecord
from court_hrms.utils.app_logger import get_logger


NEW_LEAVE_TABLES = {
    AnnualLeaveAccount.__tablename__,
    LeaveRecord.__tablename__,
}


def backup_database(reason: str = "schema_upgrade") -> Path | None:
    if not DATABASE_PATH.exists():
        return None

    backup_dir = DATABASE_PATH.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = (
        backup_dir / f"{DATABASE_PATH.stem}_{reason}_{timestamp}{DATABASE_PATH.suffix}"
    )
    shutil.copy2(DATABASE_PATH, backup_path)
    return backup_path


def apply_schema_upgrades() -> None:
    """Apply idempotent schema additions for UC05-UC08 without altering existing data."""
    logger = get_logger()
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    missing_leave_tables = NEW_LEAVE_TABLES - existing_tables

    if missing_leave_tables:
        backup_path = backup_database()
        logger.info(
            "Database migration started; missing_tables=%s backup=%s",
            sorted(missing_leave_tables),
            backup_path,
        )
        Base.metadata.create_all(
            bind=engine,
            tables=[
                AnnualLeaveAccount.__table__,
                LeaveRecord.__table__,
            ],
        )
        logger.info(
            "Database migration completed; created_tables=%s",
            sorted(missing_leave_tables),
        )
    else:
        logger.info("Database migration skipped; leave tables already present")

    with engine.connect() as connection:
        for table_name in (
            "admins",
            "staff_profiles",
            "service_records",
            "postings_transfers",
        ):
            if table_name in existing_tables:
                connection.execute(text(f"SELECT 1 FROM {table_name} LIMIT 1"))
