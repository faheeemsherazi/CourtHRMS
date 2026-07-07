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


class PostingTransfer(Base):
    __tablename__ = "postings_transfers"

    id = Column(Integer, primary_key=True)
    staff_id = Column(
        Integer, ForeignKey("staff_profiles.id"), nullable=False, index=True
    )
    station_name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    movement_type = Column(String, index=True)
    from_station = Column(String, index=True)
    to_station = Column(String, index=True)
    from_designation = Column(String)
    to_designation = Column(String)
    from_bps = Column(Integer)
    to_bps = Column(Integer)
    order_number = Column(String, index=True)
    order_date = Column(Date)
    issuing_authority = Column(String, index=True)
    effective_date = Column(Date)
    relieving_date = Column(Date)
    joining_date = Column(Date)
    charge_assumed_date = Column(Date)
    transfer_reason = Column(Text)
    transfer_category = Column(String, index=True)
    status = Column(String, index=True)
    is_current = Column(Boolean, default=True, nullable=False, index=True)
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

    staff = relationship("StaffProfile", back_populates="postings_transfers")
    document = relationship("OfficialDocument")
    creator = relationship("Admin")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "station_name": self.station_name,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "movement_type": self.movement_type,
            "from_station": self.from_station,
            "to_station": self.to_station,
            "from_designation": self.from_designation,
            "to_designation": self.to_designation,
            "from_bps": self.from_bps,
            "to_bps": self.to_bps,
            "order_number": self.order_number,
            "order_date": self.order_date,
            "issuing_authority": self.issuing_authority,
            "effective_date": self.effective_date,
            "relieving_date": self.relieving_date,
            "joining_date": self.joining_date,
            "charge_assumed_date": self.charge_assumed_date,
            "transfer_reason": self.transfer_reason,
            "transfer_category": self.transfer_category,
            "status": self.status,
            "is_current": self.is_current,
            "remarks": self.remarks,
            "document_id": self.document_id,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
