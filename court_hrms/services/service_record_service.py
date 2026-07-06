from __future__ import annotations

from sqlalchemy.orm import Session

from court_hrms.models.service_record import ServiceRecord
from court_hrms.repositories.service_record_repository import ServiceRecordRepository
from court_hrms.repositories.staff_repository import StaffRepository
from court_hrms.utils.date_utils import coerce_date
from court_hrms.utils.validators import (
    EMPLOYMENT_STATUSES,
    EMPLOYMENT_TYPES,
    ValidationError,
    clean_text,
    optional_text,
    require_text,
    validate_bps,
    validate_choice,
    validate_designation_bps,
)


class ServiceRecordService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = ServiceRecordRepository(session)
        self.staff_repository = StaffRepository(session)

    def count_records(self) -> int:
        return self.repository.count()

    def list_records(self) -> list[ServiceRecord]:
        return self.repository.list_all()

    def latest_for_staff(self, staff_id: int) -> ServiceRecord | None:
        return self.repository.latest_for_staff(staff_id)

    def create_record(self, data: dict) -> ServiceRecord:
        payload = self._validate_payload(data)
        record = ServiceRecord(**payload)
        return self.repository.add(record)

    def update_record(self, record_id: int, data: dict) -> ServiceRecord:
        record = self.repository.get_by_id(record_id)
        if record is None:
            raise ValidationError("Service record was not found.")

        payload = self._validate_payload(data)
        for field, value in payload.items():
            setattr(record, field, value)
        self.session.flush()
        return record

    def _validate_payload(self, data: dict) -> dict:
        errors: list[str] = []

        staff_id = data.get("staff_id")
        staff = None
        try:
            staff_id = int(staff_id)
            staff = self.staff_repository.get_by_id(staff_id)
        except (TypeError, ValueError):
            staff_id = None
        if staff is None:
            errors.append(
                "Staff profile must already exist before adding a service record."
            )

        designation = require_text(data, "designation", "Designation", errors)
        bps = validate_bps(data.get("bps"), errors)
        employment_type = validate_choice(
            clean_text(data.get("employment_type")),
            EMPLOYMENT_TYPES,
            "Employment type",
            errors,
        )
        employment_status = validate_choice(
            clean_text(data.get("employment_status")),
            EMPLOYMENT_STATUSES,
            "Employment status",
            errors,
        )

        try:
            date_first_appointment = coerce_date(
                data.get("date_first_appointment"),
                "Date of first appointment",
            )
        except ValueError as exc:
            date_first_appointment = None
            errors.append(str(exc))

        date_current_promotion = None
        raw_promotion_date = data.get("date_current_promotion")
        if raw_promotion_date not in (None, ""):
            try:
                date_current_promotion = coerce_date(
                    raw_promotion_date,
                    "Date of current promotion",
                )
            except ValueError as exc:
                errors.append(str(exc))

        if date_first_appointment and date_current_promotion:
            if date_current_promotion < date_first_appointment:
                errors.append(
                    "Date of current promotion cannot be before date of first appointment."
                )

        validate_designation_bps(designation, bps, errors)

        merit_number = None
        raw_merit = data.get("selection_merit_number")
        if raw_merit not in (None, ""):
            try:
                merit_number = int(raw_merit)
                if merit_number < 0:
                    errors.append("Selection merit number cannot be negative.")
            except (TypeError, ValueError):
                errors.append("Selection merit number must be a whole number.")

        if errors:
            raise ValidationError(errors)

        return {
            "staff_id": staff_id,
            "designation": designation,
            "bps": bps,
            "employment_type": employment_type,
            "employment_status": employment_status,
            "date_first_appointment": date_first_appointment,
            "date_current_promotion": date_current_promotion,
            "selection_merit_number": merit_number,
            "remarks": optional_text(data, "remarks"),
        }
