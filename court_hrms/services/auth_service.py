from __future__ import annotations

import bcrypt
from sqlalchemy.orm import Session

from court_hrms.repositories.admin_repository import AdminRepository


class AuthService:
    def __init__(self, session: Session):
        self.admin_repository = AdminRepository(session)

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )

    def authenticate(self, username: str, password: str):
        username = (username or "").strip()
        password = password or ""
        if not username or not password:
            return None

        admin = self.admin_repository.get_by_username(username)
        if admin is None:
            return None

        if not self.verify_password(password, admin.password_hash):
            return None
        return admin

