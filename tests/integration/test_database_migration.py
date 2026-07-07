from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine, func, inspect, select, text

from court_hrms.database import migrations
from court_hrms.models import Admin, PostingTransfer, ServiceRecord, StaffProfile


class DatabaseMigrationIntegrationTest(unittest.TestCase):
    def test_schema_upgrade_adds_leave_tables_without_removing_existing_records(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "old.sqlite3"
            engine = create_engine(f"sqlite:///{db_path}", future=True)
            for table in [
                Admin.__table__,
                StaffProfile.__table__,
                ServiceRecord.__table__,
                PostingTransfer.__table__,
            ]:
                table.create(bind=engine)
            with engine.begin() as connection:
                connection.execute(
                    Admin.__table__.insert().values(
                        username="admin",
                        password_hash="hash",
                        full_name="System Admin",
                    )
                )

            with patch.object(migrations, "engine", engine), patch.object(
                migrations,
                "DATABASE_PATH",
                db_path,
            ):
                migrations.apply_schema_upgrades()
                migrations.apply_schema_upgrades()

            inspector = inspect(engine)
            self.assertIn("annual_leave_accounts", inspector.get_table_names())
            self.assertIn("leave_records", inspector.get_table_names())
            for table_name in [
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
            ]:
                self.assertIn(table_name, inspector.get_table_names())

            staff_columns = {
                column["name"] for column in inspector.get_columns("staff_profiles")
            }
            self.assertIn("service_book_number", staff_columns)
            self.assertIn("date_of_joining_government_service", staff_columns)
            self.assertIn("record_status", staff_columns)
            posting_columns = {
                column["name"] for column in inspector.get_columns("postings_transfers")
            }
            self.assertIn("movement_type", posting_columns)
            self.assertIn("order_number", posting_columns)
            self.assertIn("joining_date", posting_columns)

            with engine.connect() as connection:
                count = connection.execute(
                    select(func.count(Admin.__table__.c.id))
                ).scalar_one()
                versions = list(
                    connection.execute(
                        text("SELECT version FROM schema_versions ORDER BY version")
                    ).scalars()
                )
                leave_type_count = connection.execute(
                    text("SELECT COUNT(*) FROM leave_types WHERE code='ANNUAL_LEGACY'")
                ).scalar_one()
                leave_policy_count = connection.execute(
                    text(
                        "SELECT COUNT(*) FROM leave_policies "
                        "WHERE policy_name='Legacy Annual Leave - 25 Days'"
                    )
                ).scalar_one()
            self.assertEqual(count, 1)
            self.assertEqual(versions, [1, 2, 3, 4, 5])
            self.assertEqual(leave_type_count, 1)
            self.assertEqual(leave_policy_count, 1)
            backups = list((db_path.parent / "backups").glob("*.sqlite3"))
            self.assertTrue(backups)
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
