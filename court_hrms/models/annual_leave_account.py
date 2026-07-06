from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from court_hrms.database.db import Base
from court_hrms.utils.time_utils import utc_now


class AnnualLeaveAccount(Base):
    __tablename__ = "annual_leave_accounts"
    __table_args__ = (
        UniqueConstraint("staff_id", "leave_year", name="uq_leave_account_staff_year"),
        CheckConstraint(
            "leave_year BETWEEN 1900 AND 9999", name="ck_leave_account_year"
        ),
        CheckConstraint(
            "entitlement_days >= 0", name="ck_leave_account_entitlement_non_negative"
        ),
        CheckConstraint(
            "availed_days >= 0", name="ck_leave_account_availed_non_negative"
        ),
        CheckConstraint(
            "availed_days <= entitlement_days", name="ck_leave_account_balance"
        ),
    )

    id = Column(Integer, primary_key=True)
    staff_id = Column(
        Integer,
        ForeignKey("staff_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    leave_year = Column(Integer, nullable=False, index=True)
    entitlement_days = Column(Integer, nullable=False, default=25)
    availed_days = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    staff = relationship("StaffProfile", back_populates="annual_leave_accounts")
    leave_records = relationship("LeaveRecord", back_populates="leave_account")

    @property
    def remaining_days(self) -> int:
        return int(self.entitlement_days or 0) - int(self.availed_days or 0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "leave_year": self.leave_year,
            "entitlement_days": self.entitlement_days,
            "availed_days": self.availed_days,
            "remaining_days": self.remaining_days,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
