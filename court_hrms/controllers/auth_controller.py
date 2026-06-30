from __future__ import annotations

from court_hrms.database.db import session_scope
from court_hrms.services.auth_service import AuthService


class AuthController:
    def login(self, username: str, password: str) -> tuple[bool, str, dict | None]:
        with session_scope() as session:
            admin = AuthService(session).authenticate(username, password)
            if admin is None:
                return False, "Invalid credentials.", None
            return True, "Login successful.", admin.to_dict()

