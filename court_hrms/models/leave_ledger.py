from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from court_hrms.database.db import Base
from court_hrms.utils.time_utils import utc_now


class LeaveLedgerEntry(Base):
    __tablename__ = "leave_ledger_entries"

    id = Column(Integer, primary_key=True)
    staff_id = Column(
        Integer,
        ForeignKey("staff_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    leave_type_id = Column(
        Integer,
        ForeignKey("leave_types.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    leave_account_id = Column(
        Integer,
        ForeignKey("annual_leave_accounts.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    entry_date = Column(Date, nullable=False, index=True)
    entry_type = Column(String, nullable=False, index=True)
    credit_days = Column(Integer, default=0, nullable=False)
    debit_days = Column(Integer, default=0, nullable=False)
    balance_after = Column(Integer, nullable=False)
    reference = Column(String)
    order_number = Column(String, index=True)
    remarks = Column(Text)
    created_by = Column(
        Integer,
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at = Column(DateTime, default=utc_now, nullable=False)

    staff = relationship("StaffProfile")
    leave_type = relationship("LeaveType")
    leave_account = relationship("AnnualLeaveAccount")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "leave_type_id": self.leave_type_id,
            "leave_account_id": self.leave_account_id,
            "entry_date": self.entry_date,
            "entry_type": self.entry_type,
            "credit_days": self.credit_days,
            "debit_days": self.debit_days,
            "balance_after": self.balance_after,
            "reference": self.reference,
            "order_number": self.order_number,
            "remarks": self.remarks,
            "created_by": self.created_by,
            "created_at": self.created_at,
        }
