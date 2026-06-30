from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String

from court_hrms.database.db import Base
from court_hrms.utils.time_utils import utc_now


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "created_at": self.created_at,
        }
