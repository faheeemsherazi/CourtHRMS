from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from court_hrms.database.db import Base


class PostingTransfer(Base):
    __tablename__ = "postings_transfers"

    id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey("staff_profiles.id"), nullable=False, index=True)
    station_name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    transfer_reason = Column(Text)
    is_current = Column(Boolean, default=True, nullable=False, index=True)
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    staff = relationship("StaffProfile", back_populates="postings_transfers")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "station_name": self.station_name,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "transfer_reason": self.transfer_reason,
            "is_current": self.is_current,
            "remarks": self.remarks,
            "created_at": self.created_at,
        }

