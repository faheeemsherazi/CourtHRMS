from __future__ import annotations

from court_hrms.database.db import session_scope
from court_hrms.services.auth_service import AuthService
from court_hrms.utils.app_logger import get_logger


class AuthController:
    def __init__(self):
        self.logger = get_logger()

    def login(self, username: str, password: str) -> tuple[bool, str, dict | None]:
        with session_scope() as session:
            admin = AuthService(session).authenticate(username, password)
            if admin is None:
                self.logger.warning(
                    "Login failed; username=%s", (username or "").strip()
                )
                return False, "Invalid credentials.", None
            self.logger.info("Login successful; admin_id=%s", admin.id)
            return True, "Login successful.", admin.to_dict()
