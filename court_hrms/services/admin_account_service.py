from __future__ import annotations

import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from court_hrms.repositories.admin_repository import AdminRepository
from court_hrms.services.auth_service import AuthService
from court_hrms.utils.validators import ValidationError, clean_text


class AdminAccountService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = AdminRepository(session)

    def get_admin(self, admin_id: int):
        return self.repository.get_by_id(admin_id)

    def update_account(self, admin_id: int, data: dict):
        admin = self.repository.get_by_id(admin_id)
        if admin is None:
            raise ValidationError("Administrator account was not found.")

        errors: list[str] = []
        current_password = data.get("current_password") or ""
        username = clean_text(data.get("username"))
        full_name = clean_text(data.get("full_name"))
        new_password = data.get("new_password") or ""
        confirm_password = data.get("confirm_password") or ""

        if not username:
            errors.append("Username is required.")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters.")

        if not current_password:
            errors.append("Current password is required.")
        elif not AuthService.verify_password(current_password, admin.password_hash):
            errors.append("Current password is incorrect.")

        if new_password or confirm_password:
            if len(new_password) < 8:
                errors.append("New password must be at least 8 characters.")
            if new_password != confirm_password:
                errors.append("New password and confirmation do not match.")

        if username:
            existing = self.repository.get_by_username(username)
            if existing and existing.id != admin_id:
                errors.append("Username already exists.")

        if errors:
            raise ValidationError(errors)

        admin.username = username
        admin.full_name = full_name
        if new_password:
            admin.password_hash = bcrypt.hashpw(
                new_password.encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8")

        try:
            self.session.flush()
        except IntegrityError as exc:
            raise ValidationError("Username already exists.") from exc
        return admin
