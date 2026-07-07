from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import inspect, text

from court_hrms.database.db import Base, DATABASE_PATH, engine
from court_hrms.models.annual_leave_account import AnnualLeaveAccount
from court_hrms.models.audit_event import AuditEvent
from court_hrms.models.leave_application import LeaveApplication
from court_hrms.models.leave_ledger import LeaveLedgerEntry
from court_hrms.models.leave_policy import LeavePolicy, LeaveType
from court_hrms.models.leave_record import LeaveRecord
from court_hrms.models.master_data import AppSetting, MasterDataItem
from court_hrms.models.official_document import OfficialDocument
from court_hrms.models.schema_version import SchemaVersion
from court_hrms.models.seniority_workflow import (
    SeniorityDecision,
    SeniorityList,
    SeniorityListEntry,
    SeniorityObjection,
)
from court_hrms.models.service_event import ServiceEvent
from court_hrms.utils.app_logger import get_logger


NEW_LEAVE_TABLES = {
    AnnualLeaveAccount.__tablename__,
    LeaveRecord.__tablename__,
}

FOUNDATION_TABLES = [
    SchemaVersion.__table__,
    OfficialDocument.__table__,
    ServiceEvent.__table__,
    AuditEvent.__table__,
    MasterDataItem.__table__,
    AppSetting.__table__,
]

FOUNDATION_TABLE_NAMES = {table.name for table in FOUNDATION_TABLES}

LEAVE_POLICY_TABLES = [
    LeaveType.__table__,
    LeavePolicy.__table__,
    LeaveApplication.__table__,
    LeaveLedgerEntry.__table__,
]

LEAVE_POLICY_TABLE_NAMES = {table.name for table in LEAVE_POLICY_TABLES}

SENIORITY_WORKFLOW_TABLES = [
    SeniorityList.__table__,
    SeniorityListEntry.__table__,
    SeniorityObjection.__table__,
    SeniorityDecision.__table__,
]

SENIORITY_WORKFLOW_TABLE_NAMES = {table.name for table in SENIORITY_WORKFLOW_TABLES}

STAFF_PROFILE_ADDED_COLUMNS = {
    "employee_photo_path": "TEXT",
    "employee_category": "VARCHAR",
    "cadre": "VARCHAR",
    "appointment_quota": "VARCHAR",
    "appointment_mode": "VARCHAR",
    "nationality": "VARCHAR",
    "blood_group": "VARCHAR",
    "identification_mark": "TEXT",
    "next_of_kin_name": "VARCHAR",
    "next_of_kin_relation": "VARCHAR",
    "next_of_kin_contact": "VARCHAR",
    "service_book_number": "VARCHAR",
    "service_book_volume": "VARCHAR",
    "service_book_page": "VARCHAR",
    "gp_fund_number": "VARCHAR",
    "pension_reference_number": "VARCHAR",
    "computerized_personnel_number": "VARCHAR",
    "date_of_joining_government_service": "DATE",
    "date_of_joining_district_judiciary": "DATE",
    "confirmation_date": "DATE",
    "regularization_date": "DATE",
    "probation_end_date": "DATE",
    "retirement_type": "VARCHAR",
    "actual_retirement_date": "DATE",
    "record_status": "VARCHAR",
}

STAFF_PROFILE_ADDED_INDEXES = {
    "ix_staff_profiles_service_book_number": "service_book_number",
    "ix_staff_profiles_gp_fund_number": "gp_fund_number",
    "ix_staff_profiles_pension_reference_number": "pension_reference_number",
    "ix_staff_profiles_computerized_personnel_number": (
        "computerized_personnel_number"
    ),
}

POSTING_TRANSFER_ADDED_COLUMNS = {
    "movement_type": "VARCHAR",
    "from_station": "VARCHAR",
    "to_station": "VARCHAR",
    "from_designation": "VARCHAR",
    "to_designation": "VARCHAR",
    "from_bps": "INTEGER",
    "to_bps": "INTEGER",
    "order_number": "VARCHAR",
    "order_date": "DATE",
    "issuing_authority": "VARCHAR",
    "effective_date": "DATE",
    "relieving_date": "DATE",
    "joining_date": "DATE",
    "charge_assumed_date": "DATE",
    "transfer_category": "VARCHAR",
    "status": "VARCHAR",
    "document_id": "INTEGER",
    "created_by": "INTEGER",
    "updated_at": "DATETIME",
}

POSTING_TRANSFER_ADDED_INDEXES = {
    "ix_postings_transfers_movement_type": "movement_type",
    "ix_postings_transfers_from_station": "from_station",
    "ix_postings_transfers_to_station": "to_station",
    "ix_postings_transfers_order_number": "order_number",
    "ix_postings_transfers_issuing_authority": "issuing_authority",
    "ix_postings_transfers_transfer_category": "transfer_category",
    "ix_postings_transfers_status": "status",
    "ix_postings_transfers_document_id": "document_id",
    "ix_postings_transfers_created_by": "created_by",
}


def backup_database(reason: str = "schema_upgrade") -> Path | None:
    if not DATABASE_PATH.exists():
        return None

    backup_dir = DATABASE_PATH.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_path = (
        backup_dir / f"{DATABASE_PATH.stem}_{reason}_{timestamp}{DATABASE_PATH.suffix}"
    )
    shutil.copy2(DATABASE_PATH, backup_path)
    return backup_path


def apply_schema_upgrades() -> None:
    """Apply idempotent additive schema upgrades without altering existing data."""
    logger = get_logger()
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    missing_leave_tables = NEW_LEAVE_TABLES - existing_tables
    missing_foundation_tables = FOUNDATION_TABLE_NAMES - existing_tables
    missing_leave_policy_tables = LEAVE_POLICY_TABLE_NAMES - existing_tables
    missing_seniority_workflow_tables = SENIORITY_WORKFLOW_TABLE_NAMES - existing_tables
    missing_staff_columns = _missing_staff_columns(inspector)
    missing_posting_columns = _missing_posting_columns(inspector)
    schema_version_missing = SchemaVersion.__tablename__ not in existing_tables

    needs_migration = bool(
        missing_leave_tables
        or missing_foundation_tables
        or missing_leave_policy_tables
        or missing_seniority_workflow_tables
        or missing_staff_columns
        or missing_posting_columns
        or schema_version_missing
    )
    if needs_migration:
        backup_path = backup_database()
        logger.info(
            "Database migration started; missing_leave_tables=%s "
            "missing_foundation_tables=%s missing_leave_policy_tables=%s "
            "missing_seniority_workflow_tables=%s missing_staff_columns=%s "
            "missing_posting_columns=%s backup=%s",
            sorted(missing_leave_tables),
            sorted(missing_foundation_tables),
            sorted(missing_leave_policy_tables),
            sorted(missing_seniority_workflow_tables),
            sorted(missing_staff_columns),
            sorted(missing_posting_columns),
            backup_path,
        )

        SchemaVersion.__table__.create(bind=engine, checkfirst=True)

        if missing_leave_tables:
            Base.metadata.create_all(
                bind=engine,
                tables=[
                    AnnualLeaveAccount.__table__,
                    LeaveRecord.__table__,
                ],
            )

        if missing_foundation_tables:
            Base.metadata.create_all(bind=engine, tables=FOUNDATION_TABLES)

        if missing_leave_policy_tables:
            Base.metadata.create_all(bind=engine, tables=LEAVE_POLICY_TABLES)

        if missing_seniority_workflow_tables:
            Base.metadata.create_all(bind=engine, tables=SENIORITY_WORKFLOW_TABLES)

        if missing_staff_columns:
            _add_staff_profile_columns(missing_staff_columns)

        if missing_posting_columns:
            _add_posting_transfer_columns(missing_posting_columns)

        _record_schema_version(
            1,
            "UC05-UC08 leave and reporting schema",
            "Annual leave account and leave record tables.",
        )
        _record_schema_version(
            2,
            "Government HRMS foundation schema",
            "Schema versioning, official documents, service events, audit events, "
            "master data, app settings and government-service profile fields.",
        )
        _record_schema_version(
            3,
            "Professional posting and transfer schema",
            "Official movement, order, relieving, joining and document reference fields.",
        )
        _seed_legacy_leave_policy()
        _record_schema_version(
            4,
            "Configurable leave policy and ledger schema",
            "Leave types, policies, applications and append-only ledger entries.",
        )
        _record_schema_version(
            5,
            "Seniority workflow schema",
            "Seniority list snapshots, entries, objections and decisions.",
        )
        logger.info("Database migration completed")
    else:
        logger.info("Database migration skipped; schema already current")

    with engine.connect() as connection:
        inspector = inspect(connection)
        existing_tables = set(inspector.get_table_names())
        for table_name in (
            "admins",
            "staff_profiles",
            "service_records",
            "postings_transfers",
            "annual_leave_accounts",
            "leave_records",
            "schema_versions",
            "official_documents",
            "service_events",
            "audit_events",
            "master_data_items",
            "app_settings",
            "leave_types",
            "leave_policies",
            "leave_applications",
            "leave_ledger_entries",
            "seniority_lists",
            "seniority_list_entries",
            "seniority_objections",
            "seniority_decisions",
        ):
            if table_name in existing_tables:
                connection.execute(text(f"SELECT 1 FROM {table_name} LIMIT 1"))


def _missing_staff_columns(inspector) -> set[str]:
    return _missing_columns(inspector, "staff_profiles", STAFF_PROFILE_ADDED_COLUMNS)


def _missing_posting_columns(inspector) -> set[str]:
    return _missing_columns(
        inspector,
        "postings_transfers",
        POSTING_TRANSFER_ADDED_COLUMNS,
    )


def _missing_columns(
    inspector, table_name: str, expected_columns: dict[str, str]
) -> set[str]:
    table_names = set(inspector.get_table_names())
    if table_name not in table_names:
        return set()

    current_columns = {column["name"] for column in inspector.get_columns(table_name)}
    return set(expected_columns) - current_columns


def _add_staff_profile_columns(missing_columns: set[str]) -> None:
    with engine.begin() as connection:
        for column_name in sorted(missing_columns):
            column_type = STAFF_PROFILE_ADDED_COLUMNS[column_name]
            connection.execute(
                text(
                    f"ALTER TABLE staff_profiles ADD COLUMN {column_name} {column_type}"
                )
            )
        for index_name, column_name in STAFF_PROFILE_ADDED_INDEXES.items():
            connection.execute(
                text(
                    f"CREATE INDEX IF NOT EXISTS {index_name} "
                    f"ON staff_profiles ({column_name})"
                )
            )


def _add_posting_transfer_columns(missing_columns: set[str]) -> None:
    with engine.begin() as connection:
        for column_name in sorted(missing_columns):
            column_type = POSTING_TRANSFER_ADDED_COLUMNS[column_name]
            connection.execute(
                text(
                    f"ALTER TABLE postings_transfers ADD COLUMN "
                    f"{column_name} {column_type}"
                )
            )
        connection.execute(
            text(
                "UPDATE postings_transfers SET "
                "movement_type = COALESCE(movement_type, "
                "CASE WHEN transfer_reason IS NULL OR transfer_reason = '' "
                "THEN 'First Posting' ELSE 'Transfer' END), "
                "to_station = COALESCE(to_station, station_name), "
                "effective_date = COALESCE(effective_date, start_date), "
                "status = COALESCE(status, 'Completed'), "
                "updated_at = COALESCE(updated_at, created_at)"
            )
        )
        for index_name, column_name in POSTING_TRANSFER_ADDED_INDEXES.items():
            connection.execute(
                text(
                    f"CREATE INDEX IF NOT EXISTS {index_name} "
                    f"ON postings_transfers ({column_name})"
                )
            )


def _record_schema_version(version: int, name: str, description: str) -> None:
    with engine.begin() as connection:
        exists = connection.execute(
            text("SELECT 1 FROM schema_versions WHERE version = :version"),
            {"version": version},
        ).scalar_one_or_none()
        if exists:
            return
        connection.execute(
            text(
                "INSERT INTO schema_versions "
                "(version, name, description, applied_at) "
                "VALUES (:version, :name, :description, :applied_at)"
            ),
            {
                "version": version,
                "name": name,
                "description": description,
                "applied_at": datetime.now(UTC).replace(tzinfo=None),
            },
        )


def _seed_legacy_leave_policy() -> None:
    with engine.begin() as connection:
        leave_type_id = connection.execute(
            text("SELECT id FROM leave_types WHERE code = :code"),
            {"code": "ANNUAL_LEGACY"},
        ).scalar_one_or_none()
        now_value = datetime.now(UTC).replace(tzinfo=None)
        if leave_type_id is None:
            result = connection.execute(
                text(
                    "INSERT INTO leave_types "
                    "(code, name, description, is_paid, pay_fraction, "
                    "requires_medical_certificate, requires_attachment, "
                    "debit_multiplier, is_debited_from_account, is_active, created_at) "
                    "VALUES (:code, :name, :description, 1, 1.0, 0, 0, 1.0, 1, 1, :created_at)"
                ),
                {
                    "code": "ANNUAL_LEGACY",
                    "name": "Annual Leave (Legacy SRS)",
                    "description": (
                        "Current District Court Orakzai HRMS SRS annual leave "
                        "policy used by the legacy UC05 screen."
                    ),
                    "created_at": now_value,
                },
            )
            leave_type_id = result.lastrowid

        exists = connection.execute(
            text(
                "SELECT 1 FROM leave_policies "
                "WHERE leave_type_id = :leave_type_id AND policy_name = :policy_name"
            ),
            {
                "leave_type_id": leave_type_id,
                "policy_name": "Legacy Annual Leave - 25 Days",
            },
        ).scalar_one_or_none()
        if exists:
            return
        connection.execute(
            text(
                "INSERT INTO leave_policies "
                "(leave_type_id, policy_name, entitlement_days, allow_cross_year, "
                "carry_forward_allowed, is_active, created_at, updated_at) "
                "VALUES (:leave_type_id, :policy_name, 25, 0, 0, 1, :created_at, :updated_at)"
            ),
            {
                "leave_type_id": leave_type_id,
                "policy_name": "Legacy Annual Leave - 25 Days",
                "created_at": now_value,
                "updated_at": now_value,
            },
        )
