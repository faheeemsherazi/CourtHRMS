from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine, func, inspect, select

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
            with engine.connect() as connection:
                count = connection.execute(
                    select(func.count(Admin.__table__.c.id))
                ).scalar_one()
            self.assertEqual(count, 1)
            backups = list((db_path.parent / "backups").glob("*.sqlite3"))
            self.assertTrue(backups)
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
