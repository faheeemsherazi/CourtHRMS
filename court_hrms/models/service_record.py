from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from court_hrms.database.db import Base
from court_hrms.utils.time_utils import utc_now


class ServiceRecord(Base):
    __tablename__ = "service_records"

    id = Column(Integer, primary_key=True)
    staff_id = Column(
        Integer, ForeignKey("staff_profiles.id"), nullable=False, index=True
    )
    designation = Column(String, nullable=False)
    bps = Column(Integer, nullable=False)
    employment_type = Column(String, nullable=False)
    employment_status = Column(String, nullable=False)
    date_first_appointment = Column(Date, nullable=False)
    date_current_promotion = Column(Date)
    selection_merit_number = Column(Integer)
    remarks = Column(Text)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    staff = relationship("StaffProfile", back_populates="service_records")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "designation": self.designation,
            "bps": self.bps,
            "employment_type": self.employment_type,
            "employment_status": self.employment_status,
            "date_first_appointment": self.date_first_appointment,
            "date_current_promotion": self.date_current_promotion,
            "selection_merit_number": self.selection_merit_number,
            "remarks": self.remarks,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
