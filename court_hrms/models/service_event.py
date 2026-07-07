from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from court_hrms.database.db import Base
from court_hrms.utils.time_utils import utc_now


class ServiceEvent(Base):
    __tablename__ = "service_events"

    id = Column(Integer, primary_key=True)
    staff_id = Column(
        Integer,
        ForeignKey("staff_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    event_type = Column(String, nullable=False, index=True)
    effective_date = Column(Date, nullable=False, index=True)
    order_number = Column(String, index=True)
    order_date = Column(Date)
    issuing_authority = Column(String, index=True)
    previous_designation = Column(String)
    new_designation = Column(String)
    previous_bps = Column(Integer)
    new_bps = Column(Integer)
    previous_status = Column(String)
    new_status = Column(String)
    station = Column(String, index=True)
    description = Column(Text)
    remarks = Column(Text)
    document_id = Column(
        Integer,
        ForeignKey("official_documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by = Column(
        Integer,
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    is_cancelled = Column(Boolean, default=False, nullable=False, index=True)
    cancelled_at = Column(DateTime)
    cancellation_reason = Column(Text)

    staff = relationship("StaffProfile", back_populates="service_events")
    document = relationship("OfficialDocument")
    creator = relationship("Admin")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "event_type": self.event_type,
            "effective_date": self.effective_date,
            "order_number": self.order_number,
            "order_date": self.order_date,
            "issuing_authority": self.issuing_authority,
            "previous_designation": self.previous_designation,
            "new_designation": self.new_designation,
            "previous_bps": self.previous_bps,
            "new_bps": self.new_bps,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "station": self.station,
            "description": self.description,
            "remarks": self.remarks,
            "document_id": self.document_id,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_cancelled": self.is_cancelled,
            "cancelled_at": self.cancelled_at,
            "cancellation_reason": self.cancellation_reason,
        }
