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


class LeaveApplication(Base):
    __tablename__ = "leave_applications"

    id = Column(Integer, primary_key=True)
    application_number = Column(String, unique=True, nullable=False, index=True)
    application_date = Column(Date, nullable=False)
    staff_id = Column(
        Integer,
        ForeignKey("staff_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    leave_type_id = Column(
        Integer,
        ForeignKey("leave_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    requested_start_date = Column(Date, nullable=False)
    requested_end_date = Column(Date, nullable=False)
    requested_days = Column(Integer, nullable=False)
    sanctioned_start_date = Column(Date)
    sanctioned_end_date = Column(Date)
    sanctioned_days = Column(Integer)
    prefix_holidays = Column(Integer, default=0, nullable=False)
    suffix_holidays = Column(Integer, default=0, nullable=False)
    medical_certificate_required = Column(Boolean, default=False, nullable=False)
    medical_certificate_document_id = Column(
        Integer,
        ForeignKey("official_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    reason = Column(Text)
    address_during_leave = Column(Text)
    contact_during_leave = Column(String)
    station_leaving_permission = Column(Boolean, default=False, nullable=False)
    competent_authority = Column(String)
    sanction_order_number = Column(String, index=True)
    sanction_order_date = Column(Date)
    sanction_document_id = Column(
        Integer,
        ForeignKey("official_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    status = Column(String, nullable=False, default="Draft", index=True)
    rejection_reason = Column(Text)
    resumption_date = Column(Date)
    joining_report_document_id = Column(
        Integer,
        ForeignKey("official_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_by = Column(
        Integer,
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    staff = relationship("StaffProfile")
    leave_type = relationship("LeaveType")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "application_number": self.application_number,
            "application_date": self.application_date,
            "staff_id": self.staff_id,
            "leave_type_id": self.leave_type_id,
            "requested_start_date": self.requested_start_date,
            "requested_end_date": self.requested_end_date,
            "requested_days": self.requested_days,
            "sanctioned_start_date": self.sanctioned_start_date,
            "sanctioned_end_date": self.sanctioned_end_date,
            "sanctioned_days": self.sanctioned_days,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
