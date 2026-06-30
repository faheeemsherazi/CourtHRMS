from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from court_hrms.models.admin import Admin


class AdminRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, admin_id: int) -> Admin | None:
        return self.session.get(Admin, admin_id)

    def get_by_username(self, username: str) -> Admin | None:
        stmt = select(Admin).where(Admin.username == username)
        return self.session.execute(stmt).scalar_one_or_none()

    def count(self) -> int:
        stmt = select(func.count(Admin.id))
        return int(self.session.execute(stmt).scalar_one())

    def add(self, admin: Admin) -> Admin:
        self.session.add(admin)
        self.session.flush()
        return admin
