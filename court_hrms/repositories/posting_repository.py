from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from court_hrms.models.posting_transfer import PostingTransfer


class PostingRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, posting: PostingTransfer) -> PostingTransfer:
        self.session.add(posting)
        self.session.flush()
        return posting

    def get_by_id(self, posting_id: int) -> PostingTransfer | None:
        return self.session.get(PostingTransfer, posting_id)

    def current_postings_for_staff(self, staff_id: int) -> list[PostingTransfer]:
        stmt = (
            select(PostingTransfer)
            .where(
                PostingTransfer.staff_id == staff_id,
                PostingTransfer.is_current.is_(True),
            )
            .order_by(PostingTransfer.start_date.desc(), PostingTransfer.id.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_current_for_staff(self, staff_id: int) -> PostingTransfer | None:
        current = self.current_postings_for_staff(staff_id)
        return current[0] if current else None

    def history_for_staff(self, staff_id: int) -> list[PostingTransfer]:
        stmt = (
            select(PostingTransfer)
            .where(PostingTransfer.staff_id == staff_id)
            .order_by(PostingTransfer.start_date.desc(), PostingTransfer.id.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def list_all(self) -> list[PostingTransfer]:
        stmt = (
            select(PostingTransfer)
            .options(joinedload(PostingTransfer.staff))
            .order_by(PostingTransfer.created_at.desc(), PostingTransfer.id.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def count_current(self) -> int:
        stmt = select(func.count(PostingTransfer.id)).where(
            PostingTransfer.is_current.is_(True)
        )
        return int(self.session.execute(stmt).scalar_one())
