from __future__ import annotations

from court_hrms.database.db import session_scope
from court_hrms.services.admin_account_service import AdminAccountService
from court_hrms.utils.validators import ValidationError


class AdminAccountController:
    def get_admin(self, admin_id: int) -> dict | None:
        with session_scope() as session:
            admin = AdminAccountService(session).get_admin(admin_id)
            return admin.to_dict() if admin else None

    def update_account(self, admin_id: int, data: dict) -> tuple[bool, str, dict | None]:
        try:
            with session_scope() as session:
                admin = AdminAccountService(session).update_account(admin_id, data)
                return True, "Administrator account updated successfully.", admin.to_dict()
        except ValidationError as exc:
            return False, str(exc), None
