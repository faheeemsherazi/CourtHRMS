from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from court_hrms.database.db import Base
from court_hrms.utils.time_utils import utc_now


class StaffProfile(Base):
    __tablename__ = "staff_profiles"

    id = Column(Integer, primary_key=True)
    personal_number = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    father_name = Column(String, nullable=False)
    cnic = Column(String, unique=True, nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String)
    religion = Column(String)
    marital_status = Column(String)
    domicile = Column(String)
    district = Column(String)
    tehsil = Column(String)
    mobile_number = Column(String)
    email = Column(String)
    present_address = Column(Text)
    permanent_address = Column(Text)
    emergency_contact = Column(String)
    qualification = Column(String)
    date_of_retirement = Column(Date)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    service_records = relationship(
        "ServiceRecord",
        back_populates="staff",
        cascade="all, delete-orphan",
    )
    postings_transfers = relationship(
        "PostingTransfer",
        back_populates="staff",
        cascade="all, delete-orphan",
    )
    annual_leave_accounts = relationship(
        "AnnualLeaveAccount",
        back_populates="staff",
        passive_deletes=True,
    )
    leave_records = relationship(
        "LeaveRecord",
        back_populates="staff",
        passive_deletes=True,
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "personal_number": self.personal_number,
            "full_name": self.full_name,
            "father_name": self.father_name,
            "cnic": self.cnic,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender,
            "religion": self.religion,
            "marital_status": self.marital_status,
            "domicile": self.domicile,
            "district": self.district,
            "tehsil": self.tehsil,
            "mobile_number": self.mobile_number,
            "email": self.email,
            "present_address": self.present_address,
            "permanent_address": self.permanent_address,
            "emergency_contact": self.emergency_contact,
            "qualification": self.qualification,
            "date_of_retirement": self.date_of_retirement,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# Imported after StaffProfile is defined so SQLAlchemy can resolve string relationships
# even when this model module is imported directly by tests or scripts.
from court_hrms.models.annual_leave_account import AnnualLeaveAccount  # noqa: E402,F401
from court_hrms.models.leave_record import LeaveRecord  # noqa: E402,F401
