from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, Text

from court_hrms.database.db import Base
from court_hrms.utils.time_utils import utc_now


class SchemaVersion(Base):
    __tablename__ = "schema_versions"

    id = Column(Integer, primary_key=True)
    version = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    applied_at = Column(DateTime, default=utc_now, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "applied_at": self.applied_at,
        }
