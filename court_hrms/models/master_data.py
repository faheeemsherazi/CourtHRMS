from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from court_hrms.database.db import Base
from court_hrms.utils.time_utils import utc_now


class MasterDataItem(Base):
    __tablename__ = "master_data_items"
    __table_args__ = (
        UniqueConstraint("category", "code", name="uq_master_data_category_code"),
    )

    id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False, index=True)
    code = Column(String, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "code": self.code,
            "display_name": self.display_name,
            "description": self.description,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class AppSetting(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True)
    setting_key = Column(String, unique=True, nullable=False, index=True)
    setting_value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "setting_key": self.setting_key,
            "setting_value": self.setting_value,
            "description": self.description,
            "updated_at": self.updated_at,
        }
