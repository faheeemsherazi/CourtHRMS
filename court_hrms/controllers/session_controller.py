from __future__ import annotations

from court_hrms.utils.app_logger import get_logger
from court_hrms.utils.exceptions import AuthenticationRequiredError


class SessionController:
    def __init__(self):
        self.active_user: dict | None = None
        self.is_authenticated = False
        self.logger = get_logger()

    def start_session(self, admin: dict) -> None:
        self.active_user = dict(admin)
        self.is_authenticated = True

    def logout(self) -> None:
        if not self.is_authenticated:
            self.logger.warning("Logout requested with no active authenticated session")
        else:
            self.logger.info(
                "Logout completed; admin_id=%s", self.active_user.get("id")
            )
        self.active_user = None
        self.is_authenticated = False

    def require_authenticated(self) -> dict:
        if not self.is_authenticated or self.active_user is None:
            raise AuthenticationRequiredError(
                "Authenticated administrator session is required. Please log in again."
            )
        return dict(self.active_user)
