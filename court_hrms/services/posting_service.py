from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from court_hrms.models.posting_transfer import PostingTransfer
from court_hrms.repositories.posting_repository import PostingRepository
from court_hrms.repositories.service_record_repository import ServiceRecordRepository
from court_hrms.repositories.staff_repository import StaffRepository
from court_hrms.utils.date_utils import coerce_date
from court_hrms.utils.master_data import MOVEMENT_STATUSES, MOVEMENT_TYPES
from court_hrms.utils.validators import ValidationError, optional_text, require_text


class PostingService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = PostingRepository(session)
        self.staff_repository = StaffRepository(session)
        self.service_record_repository = ServiceRecordRepository(session)

    def count_current_postings(self) -> int:
        return self.repository.count_current()

    def get_current_posting(self, staff_id: int) -> PostingTransfer | None:
        return self.repository.get_current_for_staff(staff_id)

    def history_for_staff(self, staff_id: int) -> list[PostingTransfer]:
        return self.repository.history_for_staff(staff_id)

    def add_first_posting(self, data: dict) -> PostingTransfer:
        staff_id, service_record = self._validate_staff_ready(data.get("staff_id"))
        payload = self._validate_posting_payload(
            data,
            station_field="station_name",
            date_field="start_date",
            date_label="Start date",
            first_appointment_date=service_record.date_first_appointment,
            default_movement_type="First Posting",
        )

        current_postings = self.repository.current_postings_for_staff(staff_id)
        if current_postings:
            raise ValidationError(
                "This staff member already has a current posting. Use transfer instead."
            )

        existing_history = self.repository.history_for_staff(staff_id)
        if existing_history:
            raise ValidationError(
                "Posting history already exists for this staff member. Use transfer instead."
            )

        posting = PostingTransfer(
            staff_id=staff_id,
            station_name=payload["station_name"],
            start_date=payload["posting_date"],
            movement_type="First Posting",
            to_station=payload["station_name"],
            to_designation=service_record.designation,
            to_bps=service_record.bps,
            order_number=payload["order_number"],
            order_date=payload["order_date"],
            issuing_authority=payload["issuing_authority"],
            effective_date=payload["effective_date"],
            joining_date=payload["joining_date"],
            charge_assumed_date=payload["charge_assumed_date"],
            transfer_reason=payload["transfer_reason"],
            transfer_category=payload["transfer_category"],
            status=payload["status"],
            remarks=payload["remarks"],
            document_id=payload["document_id"],
            created_by=payload["created_by"],
            is_current=True,
        )
        return self.repository.add(posting)

    def execute_transfer(self, data: dict) -> PostingTransfer:
        """Atomically close the current posting and insert the new current posting."""
        if self.session.in_transaction():
            return self._execute_transfer(data)

        with self.session.begin():
            return self._execute_transfer(data)

    def _execute_transfer(self, data: dict) -> PostingTransfer:
        staff_id, service_record = self._validate_staff_ready(data.get("staff_id"))
        payload = self._validate_posting_payload(
            data,
            station_field="new_station",
            date_field="transfer_date",
            date_label="Transfer date",
            first_appointment_date=service_record.date_first_appointment,
            default_movement_type="Transfer",
        )

        current_postings = self.repository.current_postings_for_staff(staff_id)
        if not current_postings:
            raise ValidationError(
                "No current posting was found. Add the first posting before transfer."
            )
        if len(current_postings) > 1:
            raise ValidationError(
                "Multiple current postings exist for this staff member. Please correct posting history first."
            )

        current_posting = current_postings[0]
        transfer_date: date = payload["posting_date"]
        if transfer_date < current_posting.start_date:
            raise ValidationError(
                "Transfer date cannot be before the current posting start date."
            )

        current_posting.end_date = payload["relieving_date"] or transfer_date
        current_posting.is_current = False

        new_posting = PostingTransfer(
            staff_id=staff_id,
            station_name=payload["station_name"],
            start_date=transfer_date,
            movement_type="Transfer",
            from_station=current_posting.station_name,
            to_station=payload["station_name"],
            from_designation=service_record.designation,
            to_designation=service_record.designation,
            from_bps=service_record.bps,
            to_bps=service_record.bps,
            order_number=payload["order_number"],
            order_date=payload["order_date"],
            issuing_authority=payload["issuing_authority"],
            effective_date=payload["effective_date"],
            relieving_date=payload["relieving_date"],
            joining_date=payload["joining_date"],
            charge_assumed_date=payload["charge_assumed_date"],
            transfer_reason=payload["transfer_reason"],
            transfer_category=payload["transfer_category"],
            status=payload["status"],
            remarks=payload["remarks"],
            document_id=payload["document_id"],
            created_by=payload["created_by"],
            is_current=True,
        )
        self.repository.add(new_posting)
        self.session.flush()
        return new_posting

    def _validate_staff_ready(self, raw_staff_id):
        try:
            staff_id = int(raw_staff_id)
        except (TypeError, ValueError) as exc:
            raise ValidationError(
                "Staff profile must be selected before posting or transfer."
            ) from exc

        staff = self.staff_repository.get_by_id(staff_id)
        if staff is None:
            raise ValidationError(
                "Staff profile must already exist before posting or transfer."
            )

        service_record = self.service_record_repository.latest_for_staff(staff_id)
        if service_record is None:
            raise ValidationError(
                "A service record must exist before posting or transfer."
            )

        return staff_id, service_record

    def _validate_posting_payload(
        self,
        data: dict,
        station_field: str,
        date_field: str,
        date_label: str,
        first_appointment_date: date,
        default_movement_type: str,
    ) -> dict:
        errors: list[str] = []
        station_name = require_text(data, station_field, "Station name", errors)

        try:
            posting_date = coerce_date(data.get(date_field), date_label)
        except ValueError as exc:
            posting_date = None
            errors.append(str(exc))

        if posting_date and posting_date < first_appointment_date:
            errors.append(f"{date_label} cannot be before date of first appointment.")

        order_date = self._optional_date(data.get("order_date"), "Order date", errors)
        effective_date = (
            self._optional_date(data.get("effective_date"), "Effective date", errors)
            or posting_date
        )
        relieving_date = self._optional_date(
            data.get("relieving_date"), "Relieving date", errors
        )
        joining_date = (
            self._optional_date(data.get("joining_date"), "Joining date", errors)
            or posting_date
        )
        charge_assumed_date = self._optional_date(
            data.get("charge_assumed_date"), "Charge assumed date", errors
        )

        movement_type = optional_text(data, "movement_type") or default_movement_type
        if movement_type not in MOVEMENT_TYPES:
            errors.append("Movement type is not valid.")

        status = optional_text(data, "status") or "Completed"
        if status not in MOVEMENT_STATUSES:
            errors.append("Movement status is not valid.")

        order_number = optional_text(data, "order_number")
        issuing_authority = optional_text(data, "issuing_authority")
        remarks = optional_text(data, "remarks")
        audit_reason = optional_text(data, "audit_reason")

        if order_date and joining_date and order_date > joining_date and not remarks:
            errors.append(
                "Transfer order date cannot be later than joining date without explanation."
            )
        if (
            order_date
            and relieving_date
            and relieving_date < order_date
            and not remarks
        ):
            errors.append(
                "Relieving date cannot precede order date without a retrospective explanation."
            )
        if relieving_date and joining_date and joining_date < relieving_date:
            errors.append("Joining date cannot be before relieving date.")

        if order_number and issuing_authority and order_date:
            if (
                self.repository.order_reference_exists(
                    order_number=order_number,
                    issuing_authority=issuing_authority,
                    order_year=order_date.year,
                )
                and not audit_reason
            ):
                errors.append(
                    "Order number already exists for this issuing authority and year. "
                    "Provide an audit reason to override."
                )

        if errors:
            raise ValidationError(errors)

        return {
            "station_name": station_name,
            "posting_date": posting_date,
            "movement_type": movement_type,
            "order_number": order_number,
            "order_date": order_date,
            "issuing_authority": issuing_authority,
            "effective_date": effective_date,
            "relieving_date": relieving_date,
            "joining_date": joining_date,
            "charge_assumed_date": charge_assumed_date,
            "transfer_reason": optional_text(data, "transfer_reason"),
            "transfer_category": optional_text(data, "transfer_category"),
            "status": status,
            "remarks": remarks,
            "document_id": self._optional_int(data.get("document_id")),
            "created_by": self._optional_int(data.get("created_by")),
        }

    @staticmethod
    def _optional_date(value, label: str, errors: list[str]) -> date | None:
        if value in (None, ""):
            return None
        try:
            return coerce_date(value, label)
        except ValueError as exc:
            errors.append(str(exc))
            return None

    @staticmethod
    def _optional_int(value) -> int | None:
        if value in (None, ""):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
