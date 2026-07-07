from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from court_hrms.database.db import Base
from court_hrms.utils.time_utils import utc_now


class LeaveType(Base):
    __tablename__ = "leave_types"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    is_paid = Column(Boolean, default=True, nullable=False)
    pay_fraction = Column(Float, default=1.0, nullable=False)
    requires_medical_certificate = Column(Boolean, default=False, nullable=False)
    requires_attachment = Column(Boolean, default=False, nullable=False)
    gender_restriction = Column(String)
    minimum_service_days = Column(Integer)
    maximum_days_per_spell = Column(Integer)
    maximum_days_entire_service = Column(Integer)
    debit_multiplier = Column(Float, default=1.0, nullable=False)
    is_debited_from_account = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    effective_from = Column(Date)
    effective_to = Column(Date)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    policies = relationship("LeavePolicy", back_populates="leave_type")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "is_paid": self.is_paid,
            "pay_fraction": self.pay_fraction,
            "requires_medical_certificate": self.requires_medical_certificate,
            "requires_attachment": self.requires_attachment,
            "gender_restriction": self.gender_restriction,
            "minimum_service_days": self.minimum_service_days,
            "maximum_days_per_spell": self.maximum_days_per_spell,
            "maximum_days_entire_service": self.maximum_days_entire_service,
            "debit_multiplier": self.debit_multiplier,
            "is_debited_from_account": self.is_debited_from_account,
            "is_active": self.is_active,
            "effective_from": self.effective_from,
            "effective_to": self.effective_to,
            "created_at": self.created_at,
        }


class LeavePolicy(Base):
    __tablename__ = "leave_policies"

    id = Column(Integer, primary_key=True)
    leave_type_id = Column(
        Integer,
        ForeignKey("leave_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    policy_name = Column(String, nullable=False)
    entitlement_days = Column(Integer, nullable=False)
    leave_year = Column(Integer, nullable=True, index=True)
    allow_cross_year = Column(Boolean, default=False, nullable=False)
    carry_forward_allowed = Column(Boolean, default=False, nullable=False)
    effective_from = Column(Date)
    effective_to = Column(Date)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    leave_type = relationship("LeaveType", back_populates="policies")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "leave_type_id": self.leave_type_id,
            "policy_name": self.policy_name,
            "entitlement_days": self.entitlement_days,
            "leave_year": self.leave_year,
            "allow_cross_year": self.allow_cross_year,
            "carry_forward_allowed": self.carry_forward_allowed,
            "effective_from": self.effective_from,
            "effective_to": self.effective_to,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
