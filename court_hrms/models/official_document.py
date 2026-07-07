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


class OfficialDocument(Base):
    __tablename__ = "official_documents"

    id = Column(Integer, primary_key=True)
    document_type = Column(String, nullable=False, index=True)
    order_number = Column(String, index=True)
    order_date = Column(Date)
    subject = Column(Text, nullable=False)
    issuing_authority = Column(String, index=True)
    reference_number = Column(String, index=True)
    received_date = Column(Date)
    effective_date = Column(Date)
    staff_id = Column(
        Integer,
        ForeignKey("staff_profiles.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    related_entity_type = Column(String, index=True)
    related_entity_id = Column(Integer, index=True)
    original_filename = Column(String)
    stored_filename = Column(String)
    stored_relative_path = Column(Text)
    mime_type = Column(String)
    file_size = Column(Integer)
    sha256_checksum = Column(String)
    remarks = Column(Text)
    created_by = Column(
        Integer,
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at = Column(DateTime, default=utc_now, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)

    staff = relationship("StaffProfile", back_populates="official_documents")
    creator = relationship("Admin")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "document_type": self.document_type,
            "order_number": self.order_number,
            "order_date": self.order_date,
            "subject": self.subject,
            "issuing_authority": self.issuing_authority,
            "reference_number": self.reference_number,
            "received_date": self.received_date,
            "effective_date": self.effective_date,
            "staff_id": self.staff_id,
            "related_entity_type": self.related_entity_type,
            "related_entity_id": self.related_entity_id,
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "stored_relative_path": self.stored_relative_path,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "sha256_checksum": self.sha256_checksum,
            "remarks": self.remarks,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "is_archived": self.is_archived,
        }
