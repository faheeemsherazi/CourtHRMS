from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


APP_FOLDER_NAME = "DistrictCourtOrakzaiHRMS"
DB_FILE_NAME = "court_hrms.sqlite3"


def get_database_path() -> Path:
    """Return a writable, local database path for development and Windows builds."""
    explicit_path = os.getenv("COURT_HRMS_DB_PATH")
    if explicit_path:
        db_path = Path(explicit_path).expanduser()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path

    if os.name == "nt":
        base_dir = Path(os.getenv("LOCALAPPDATA", Path.home()))
    else:
        base_dir = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    app_dir = base_dir / APP_FOLDER_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir / DB_FILE_NAME


DATABASE_PATH = get_database_path()
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)

Base = declarative_base()


@contextmanager
def session_scope() -> Iterator:
    """Provide a transactional SQLAlchemy session for controllers/services."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

