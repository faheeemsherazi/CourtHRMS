from __future__ import annotations

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from court_hrms.models.leave_record import LeaveRecord
from court_hrms.repositories.admin_repository import AdminRepository
from court_hrms.repositories.leave_repository import LeaveRepository
from court_hrms.repositories.service_record_repository import ServiceRecordRepository
from court_hrms.repositories.staff_repository import StaffRepository
from court_hrms.utils.app_logger import get_logger, mask_identifier
from court_hrms.utils.exceptions import (
    AuthenticationRequiredError,
    DatabaseOperationError,
    LeaveBalanceError,
    LeaveDateError,
    StaffNotFoundError,
)
from court_hrms.utils.leave_rules import (
    ANNUAL_LEAVE_ENTITLEMENT_DAYS,
    validate_leave_dates,
    validate_leave_year,
)
from court_hrms.utils.validators import ValidationError, clean_text


class LeaveService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = LeaveRepository(session)
        self.staff_repository = StaffRepository(session)
        self.service_record_repository = ServiceRecordRepository(session)
        self.admin_repository = AdminRepository(session)
        self.logger = get_logger()

    def calculate_requested_days(self, start_value, end_value) -> int:
        _start_date, _end_date, days = validate_leave_dates(start_value, end_value)
        return days

    def find_staff_context(self, personal_number: str, leave_year: int) -> dict:
        personal_number = (personal_number or "").strip()
        if not personal_number:
            raise StaffNotFoundError("Personal number is required.")

        staff = self.staff_repository.get_by_personal_number(personal_number)
        if staff is None:
            raise StaffNotFoundError("No staff profile found for this personal number.")

        latest_service_record = self.service_record_repository.latest_for_staff(
            staff.id
        )
        return {
            "staff": staff.to_dict(),
            "service_record": (
                latest_service_record.to_dict() if latest_service_record else None
            ),
            "summary": self.get_account_summary(staff.id, leave_year),
            "history": self.list_history(staff.id, leave_year),
        }

    def get_account_summary(self, staff_id: int, leave_year: int) -> dict:
        leave_year = validate_leave_year(leave_year)
        account = self.repository.get_account(staff_id, leave_year)
        if account is None:
            return {
                "id": None,
                "staff_id": staff_id,
                "leave_year": leave_year,
                "entitlement_days": ANNUAL_LEAVE_ENTITLEMENT_DAYS,
                "availed_days": 0,
                "remaining_days": ANNUAL_LEAVE_ENTITLEMENT_DAYS,
            }
        return account.to_dict()

    def list_history(self, staff_id: int, leave_year: int | None = None) -> list[dict]:
        if leave_year is not None:
            leave_year = validate_leave_year(leave_year)
        records = self.repository.list_records_for_staff(staff_id, leave_year)
        return [self._record_to_dict(record) for record in records]

    def list_account_years(self, staff_id: int) -> list[int]:
        return [
            account.leave_year
            for account in self.repository.list_accounts_for_staff(staff_id)
        ]

    def process_leave(self, data: dict) -> dict:
        transaction = (
            self.session.begin_nested()
            if self.session.in_transaction()
            else self.session.begin()
        )
        with transaction:
            return self._process_leave(data)

    def _process_leave(self, data: dict) -> dict:
        staff_id = self._require_staff_id(data.get("staff_id"))
        admin_id = self._require_admin_id(data.get("processed_by_admin_id"))
        leave_year = validate_leave_year(data.get("leave_year"))
        start_date, end_date, requested_days = validate_leave_dates(
            data.get("start_date"),
            data.get("end_date"),
        )

        if start_date.year != leave_year:
            raise LeaveDateError(
                "Leave year must match the selected start and end dates."
            )

        provided_days = data.get("days_availed")
        if provided_days not in (None, ""):
            try:
                provided_days = int(provided_days)
            except (TypeError, ValueError) as exc:
                raise LeaveDateError("Number of days must be a whole number.") from exc
            if provided_days != requested_days:
                raise LeaveDateError(
                    "Calculated number of days does not match the entered number of days."
                )

        reason = clean_text(data.get("reason"))
        if not reason:
            raise ValidationError("Reason is required.")
        remarks = clean_text(data.get("remarks"))

        try:
            account = self.repository.get_or_create_account(
                staff_id,
                leave_year,
                ANNUAL_LEAVE_ENTITLEMENT_DAYS,
            )
            remaining_days = account.remaining_days
            if requested_days > remaining_days:
                raise LeaveBalanceError(
                    "Insufficient leave balance.\n"
                    f"Requested: {requested_days} days\n"
                    f"Remaining: {remaining_days} days"
                )

            record = LeaveRecord(
                staff_id=staff_id,
                leave_account_id=account.id,
                start_date=start_date,
                end_date=end_date,
                days_availed=requested_days,
                reason=reason,
                remarks=remarks,
                processed_by_admin_id=admin_id,
            )
            self.repository.add_record(record)
            account.availed_days += requested_days
            self.session.flush()
        except (LeaveBalanceError, ValidationError):
            raise
        except IntegrityError as exc:
            raise ValidationError(
                "Leave account or leave record could not be saved."
            ) from exc
        except SQLAlchemyError as exc:
            self.logger.exception(
                "Leave transaction failed; staff_id=%s year=%s",
                staff_id,
                leave_year,
            )
            raise DatabaseOperationError("Leave transaction failed.") from exc

        self.logger.info(
            "Leave recorded; personal_number=%s year=%s days=%s remaining=%s",
            mask_identifier(self.staff_repository.get_by_id(staff_id).personal_number),
            leave_year,
            requested_days,
            account.remaining_days,
        )
        return {
            "message": (
                "Leave recorded successfully.\n"
                f"New remaining balance: {account.remaining_days} days."
            ),
            "record": self._record_to_dict(record),
            "summary": account.to_dict(),
        }

    def _require_staff_id(self, raw_staff_id) -> int:
        try:
            staff_id = int(raw_staff_id)
        except (TypeError, ValueError) as exc:
            raise StaffNotFoundError(
                "Staff profile must be selected before processing leave."
            ) from exc

        staff = self.staff_repository.get_by_id(staff_id)
        if staff is None:
            raise StaffNotFoundError("Staff profile was not found.")
        return staff_id

    def _require_admin_id(self, raw_admin_id) -> int:
        try:
            admin_id = int(raw_admin_id)
        except (TypeError, ValueError) as exc:
            raise AuthenticationRequiredError(
                "Authenticated administrator session is required. Please log in again."
            ) from exc

        if self.admin_repository.get_by_id(admin_id) is None:
            raise AuthenticationRequiredError(
                "Authenticated administrator session is required. Please log in again."
            )
        return admin_id

    @staticmethod
    def _record_to_dict(record: LeaveRecord) -> dict:
        data = record.to_dict()
        account = getattr(record, "leave_account", None)
        admin = getattr(record, "processed_by_admin", None)
        data["leave_year"] = account.leave_year if account else record.start_date.year
        data["processed_by"] = (
            admin.full_name or admin.username if admin is not None else ""
        )
        return data
