from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from court_hrms.database.db import Base
from court_hrms.utils.time_utils import utc_now


class LeaveRecord(Base):
    __tablename__ = "leave_records"
    __table_args__ = (
        CheckConstraint("days_availed > 0", name="ck_leave_record_days_positive"),
        CheckConstraint("end_date >= start_date", name="ck_leave_record_date_order"),
    )

    id = Column(Integer, primary_key=True)
    staff_id = Column(
        Integer,
        ForeignKey("staff_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    leave_account_id = Column(
        Integer,
        ForeignKey("annual_leave_accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_availed = Column(Integer, nullable=False)
    reason = Column(Text)
    remarks = Column(Text)
    processed_by_admin_id = Column(
        Integer,
        ForeignKey("admins.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    created_at = Column(DateTime, default=utc_now, nullable=False)

    staff = relationship("StaffProfile", back_populates="leave_records")
    leave_account = relationship("AnnualLeaveAccount", back_populates="leave_records")
    processed_by_admin = relationship("Admin")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "leave_account_id": self.leave_account_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "days_availed": self.days_availed,
            "reason": self.reason,
            "remarks": self.remarks,
            "processed_by_admin_id": self.processed_by_admin_id,
            "created_at": self.created_at,
        }
