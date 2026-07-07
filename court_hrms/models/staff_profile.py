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
    employee_photo_path = Column(Text)
    employee_category = Column(String)
    cadre = Column(String)
    appointment_quota = Column(String)
    appointment_mode = Column(String)
    nationality = Column(String)
    blood_group = Column(String)
    identification_mark = Column(Text)
    next_of_kin_name = Column(String)
    next_of_kin_relation = Column(String)
    next_of_kin_contact = Column(String)
    service_book_number = Column(String, index=True)
    service_book_volume = Column(String)
    service_book_page = Column(String)
    gp_fund_number = Column(String, index=True)
    pension_reference_number = Column(String, index=True)
    computerized_personnel_number = Column(String, index=True)
    date_of_joining_government_service = Column(Date)
    date_of_joining_district_judiciary = Column(Date)
    confirmation_date = Column(Date)
    regularization_date = Column(Date)
    probation_end_date = Column(Date)
    retirement_type = Column(String)
    actual_retirement_date = Column(Date)
    record_status = Column(String)
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
    official_documents = relationship(
        "OfficialDocument",
        back_populates="staff",
        passive_deletes=True,
    )
    service_events = relationship(
        "ServiceEvent",
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
            "employee_photo_path": self.employee_photo_path,
            "employee_category": self.employee_category,
            "cadre": self.cadre,
            "appointment_quota": self.appointment_quota,
            "appointment_mode": self.appointment_mode,
            "nationality": self.nationality,
            "blood_group": self.blood_group,
            "identification_mark": self.identification_mark,
            "next_of_kin_name": self.next_of_kin_name,
            "next_of_kin_relation": self.next_of_kin_relation,
            "next_of_kin_contact": self.next_of_kin_contact,
            "service_book_number": self.service_book_number,
            "service_book_volume": self.service_book_volume,
            "service_book_page": self.service_book_page,
            "gp_fund_number": self.gp_fund_number,
            "pension_reference_number": self.pension_reference_number,
            "computerized_personnel_number": self.computerized_personnel_number,
            "date_of_joining_government_service": (
                self.date_of_joining_government_service
            ),
            "date_of_joining_district_judiciary": (
                self.date_of_joining_district_judiciary
            ),
            "confirmation_date": self.confirmation_date,
            "regularization_date": self.regularization_date,
            "probation_end_date": self.probation_end_date,
            "retirement_type": self.retirement_type,
            "actual_retirement_date": self.actual_retirement_date,
            "record_status": self.record_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# Imported after StaffProfile is defined so SQLAlchemy can resolve string relationships
# even when this model module is imported directly by tests or scripts.
from court_hrms.models.annual_leave_account import AnnualLeaveAccount  # noqa: E402,F401
from court_hrms.models.leave_record import LeaveRecord  # noqa: E402,F401
from court_hrms.models.official_document import OfficialDocument  # noqa: E402,F401
from court_hrms.models.service_event import ServiceEvent  # noqa: E402,F401
