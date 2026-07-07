from __future__ import annotations

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from court_hrms.database.db import Base
from court_hrms.utils.time_utils import utc_now


class SeniorityList(Base):
    __tablename__ = "seniority_lists"
    __table_args__ = (
        UniqueConstraint(
            "designation",
            "list_year",
            "version_number",
            name="uq_seniority_list_designation_year_version",
        ),
    )

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    designation = Column(String, nullable=False, index=True)
    cadre = Column(String, index=True)
    bps = Column(Integer, index=True)
    list_year = Column(Integer, nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    list_type = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, index=True)
    cutoff_date = Column(Date)
    generated_at = Column(DateTime, default=utc_now, nullable=False)
    generated_by = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"))
    circulation_date = Column(Date)
    objection_deadline = Column(Date)
    finalized_date = Column(Date)
    finalized_by = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"))
    approval_order_number = Column(String)
    approval_order_date = Column(Date)
    remarks = Column(Text)

    entries = relationship("SeniorityListEntry", back_populates="seniority_list")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "designation": self.designation,
            "cadre": self.cadre,
            "bps": self.bps,
            "list_year": self.list_year,
            "version_number": self.version_number,
            "list_type": self.list_type,
            "status": self.status,
            "cutoff_date": self.cutoff_date,
            "generated_at": self.generated_at,
            "generated_by": self.generated_by,
            "circulation_date": self.circulation_date,
            "objection_deadline": self.objection_deadline,
            "finalized_date": self.finalized_date,
            "finalized_by": self.finalized_by,
            "approval_order_number": self.approval_order_number,
            "approval_order_date": self.approval_order_date,
            "remarks": self.remarks,
        }


class SeniorityListEntry(Base):
    __tablename__ = "seniority_list_entries"

    id = Column(Integer, primary_key=True)
    seniority_list_id = Column(
        Integer,
        ForeignKey("seniority_lists.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    staff_id = Column(Integer, ForeignKey("staff_profiles.id", ondelete="RESTRICT"))
    rank = Column(Integer, nullable=False, index=True)
    personal_number = Column(String, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    father_name = Column(String)
    qualification = Column(String)
    designation = Column(String, nullable=False)
    bps = Column(Integer)
    date_of_birth = Column(Date)
    first_government_entry = Column(Date)
    first_judiciary_entry = Column(Date)
    current_post_date = Column(Date)
    promotion_date = Column(Date)
    retirement_date = Column(Date)
    current_posting = Column(String)
    ranking_basis = Column(Text)
    remarks = Column(Text)

    seniority_list = relationship("SeniorityList", back_populates="entries")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "seniority_list_id": self.seniority_list_id,
            "staff_id": self.staff_id,
            "rank": self.rank,
            "personal_number": self.personal_number,
            "full_name": self.full_name,
            "father_name": self.father_name,
            "qualification": self.qualification,
            "designation": self.designation,
            "bps": self.bps,
            "date_of_birth": self.date_of_birth,
            "first_government_entry": self.first_government_entry,
            "first_judiciary_entry": self.first_judiciary_entry,
            "current_post_date": self.current_post_date,
            "promotion_date": self.promotion_date,
            "retirement_date": self.retirement_date,
            "current_posting": self.current_posting,
            "ranking_basis": self.ranking_basis,
            "remarks": self.remarks,
        }


class SeniorityObjection(Base):
    __tablename__ = "seniority_objections"

    id = Column(Integer, primary_key=True)
    objection_number = Column(String, unique=True, nullable=False, index=True)
    seniority_list_id = Column(
        Integer,
        ForeignKey("seniority_lists.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    staff_id = Column(Integer, ForeignKey("staff_profiles.id", ondelete="RESTRICT"))
    submitted_date = Column(Date, nullable=False)
    subject = Column(String, nullable=False)
    details = Column(Text, nullable=False)
    supporting_document_id = Column(
        Integer, ForeignKey("official_documents.id", ondelete="SET NULL")
    )
    status = Column(String, nullable=False, default="Received", index=True)
    hearing_date = Column(Date)
    decision = Column(Text)
    decision_date = Column(Date)
    decision_order_number = Column(String)
    decision_document_id = Column(
        Integer, ForeignKey("official_documents.id", ondelete="SET NULL")
    )
    disposed_by = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "objection_number": self.objection_number,
            "seniority_list_id": self.seniority_list_id,
            "staff_id": self.staff_id,
            "submitted_date": self.submitted_date,
            "subject": self.subject,
            "details": self.details,
            "status": self.status,
            "hearing_date": self.hearing_date,
            "decision": self.decision,
            "decision_date": self.decision_date,
            "decision_order_number": self.decision_order_number,
            "disposed_by": self.disposed_by,
        }


class SeniorityDecision(Base):
    __tablename__ = "seniority_decisions"

    id = Column(Integer, primary_key=True)
    seniority_objection_id = Column(
        Integer,
        ForeignKey("seniority_objections.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    decision = Column(Text, nullable=False)
    decision_date = Column(Date, nullable=False)
    decision_order_number = Column(String)
    decision_document_id = Column(
        Integer, ForeignKey("official_documents.id", ondelete="SET NULL")
    )
    disposed_by = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=utc_now, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "seniority_objection_id": self.seniority_objection_id,
            "decision": self.decision,
            "decision_date": self.decision_date,
            "decision_order_number": self.decision_order_number,
            "decision_document_id": self.decision_document_id,
            "disposed_by": self.disposed_by,
            "created_at": self.created_at,
        }
