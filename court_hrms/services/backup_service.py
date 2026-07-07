from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import create_engine, inspect, text

from court_hrms.database.db import DATABASE_PATH
from court_hrms.utils.exceptions import BackupError, RestoreError


BACKUP_EXTENSION = ".dcohrbackup"


class BackupService:
    def __init__(
        self,
        database_path: Path | None = None,
        attachments_dir: Path | None = None,
    ):
        self.database_path = Path(database_path or DATABASE_PATH)
        self.attachments_dir = attachments_dir

    def create_backup(self, output_path: str | Path) -> Path:
        output_path = self._normalise_backup_path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.database_path.exists():
            raise BackupError("Database file was not found.")

        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            backup_db = temp_dir / "court_hrms.sqlite3"
            self._sqlite_backup(self.database_path, backup_db)
            manifest = self._build_manifest(backup_db)
            manifest_path = temp_dir / "manifest.json"
            manifest_path.write_text(
                json.dumps(manifest, indent=2),
                encoding="utf-8",
            )

            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.write(backup_db, "database/court_hrms.sqlite3")
                archive.write(manifest_path, "manifest.json")
                if self.attachments_dir and self.attachments_dir.exists():
                    for path in self.attachments_dir.rglob("*"):
                        if path.is_file():
                            archive.write(
                                path,
                                f"attachments/{path.relative_to(self.attachments_dir)}",
                            )

        if not self.verify_backup(output_path):
            raise BackupError("Backup verification failed.")
        return output_path

    def verify_backup(self, backup_path: str | Path) -> bool:
        backup_path = Path(backup_path)
        if not backup_path.exists() or backup_path.stat().st_size == 0:
            return False
        try:
            with zipfile.ZipFile(backup_path, "r") as archive:
                manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
                database_bytes = archive.read("database/court_hrms.sqlite3")
        except (KeyError, OSError, json.JSONDecodeError, zipfile.BadZipFile):
            return False
        return hashlib.sha256(database_bytes).hexdigest() == manifest.get(
            "database_sha256"
        )

    def restore_backup(
        self,
        backup_path: str | Path,
        target_database_path: str | Path,
        *,
        admin_password_verified: bool = False,
    ) -> Path:
        if not admin_password_verified:
            raise RestoreError("Current admin password verification is required.")
        if not self.verify_backup(backup_path):
            raise RestoreError("Backup package verification failed.")

        target_database_path = Path(target_database_path)
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            with zipfile.ZipFile(backup_path, "r") as archive:
                archive.extract("database/court_hrms.sqlite3", temp_dir)
            restored_db = temp_dir / "database" / "court_hrms.sqlite3"
            if not self._integrity_check(restored_db):
                raise RestoreError("Restored database failed SQLite integrity check.")
            target_database_path.parent.mkdir(parents=True, exist_ok=True)
            pre_restore = target_database_path.with_suffix(
                f".pre_restore_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.sqlite3"
            )
            if target_database_path.exists():
                target_database_path.replace(pre_restore)
            restored_db.replace(target_database_path)
        return target_database_path

    @staticmethod
    def _normalise_backup_path(output_path: str | Path) -> Path:
        output_path = Path(output_path)
        if output_path.suffix.lower() != BACKUP_EXTENSION:
            output_path = output_path.with_suffix(BACKUP_EXTENSION)
        return output_path

    @staticmethod
    def _sqlite_backup(source: Path, destination: Path) -> None:
        try:
            with sqlite3.connect(source) as source_connection:
                with sqlite3.connect(destination) as destination_connection:
                    source_connection.backup(destination_connection)
        except sqlite3.Error as exc:
            raise BackupError("SQLite backup operation failed.") from exc

    def _build_manifest(self, backup_db: Path) -> dict:
        return {
            "application": "District Court Orakzai HRMS",
            "created_at_utc": datetime.now(UTC).isoformat(),
            "schema_versions": self._schema_versions(backup_db),
            "record_counts": self._record_counts(backup_db),
            "database_sha256": self._sha256(backup_db),
            "database_size_bytes": backup_db.stat().st_size,
        }

    @staticmethod
    def _sha256(path: Path) -> str:
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def _record_counts(db_path: Path) -> dict[str, int]:
        engine = create_engine(f"sqlite:///{db_path}", future=True)
        try:
            with engine.connect() as connection:
                inspector = inspect(connection)
                return {
                    table: int(
                        connection.execute(
                            text(f"SELECT COUNT(*) FROM {table}")
                        ).scalar_one()
                    )
                    for table in inspector.get_table_names()
                }
        finally:
            engine.dispose()

    @staticmethod
    def _schema_versions(db_path: Path) -> list[int]:
        engine = create_engine(f"sqlite:///{db_path}", future=True)
        try:
            with engine.connect() as connection:
                inspector = inspect(connection)
                if "schema_versions" not in inspector.get_table_names():
                    return []
                return list(
                    connection.execute(
                        text("SELECT version FROM schema_versions ORDER BY version")
                    ).scalars()
                )
        finally:
            engine.dispose()

    @staticmethod
    def _integrity_check(db_path: Path) -> bool:
        with sqlite3.connect(db_path) as connection:
            result = connection.execute("PRAGMA integrity_check").fetchone()
        return bool(result and result[0] == "ok")
