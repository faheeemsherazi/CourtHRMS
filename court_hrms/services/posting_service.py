from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from court_hrms.models.posting_transfer import PostingTransfer
from court_hrms.repositories.posting_repository import PostingRepository
from court_hrms.repositories.service_record_repository import ServiceRecordRepository
from court_hrms.repositories.staff_repository import StaffRepository
from court_hrms.utils.date_utils import coerce_date
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
        staff_id, first_appointment_date = self._validate_staff_ready(data.get("staff_id"))
        payload = self._validate_posting_payload(
            data,
            station_field="station_name",
            date_field="start_date",
            date_label="Start date",
            first_appointment_date=first_appointment_date,
        )

        current_postings = self.repository.current_postings_for_staff(staff_id)
        if current_postings:
            raise ValidationError("This staff member already has a current posting. Use transfer instead.")

        existing_history = self.repository.history_for_staff(staff_id)
        if existing_history:
            raise ValidationError("Posting history already exists for this staff member. Use transfer instead.")

        posting = PostingTransfer(
            staff_id=staff_id,
            station_name=payload["station_name"],
            start_date=payload["posting_date"],
            transfer_reason=payload["transfer_reason"],
            remarks=payload["remarks"],
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
        staff_id, first_appointment_date = self._validate_staff_ready(data.get("staff_id"))
        payload = self._validate_posting_payload(
            data,
            station_field="new_station",
            date_field="transfer_date",
            date_label="Transfer date",
            first_appointment_date=first_appointment_date,
        )

        current_postings = self.repository.current_postings_for_staff(staff_id)
        if not current_postings:
            raise ValidationError("No current posting was found. Add the first posting before transfer.")
        if len(current_postings) > 1:
            raise ValidationError(
                "Multiple current postings exist for this staff member. Please correct posting history first."
            )

        current_posting = current_postings[0]
        transfer_date: date = payload["posting_date"]
        if transfer_date < current_posting.start_date:
            raise ValidationError("Transfer date cannot be before the current posting start date.")

        current_posting.end_date = transfer_date
        current_posting.is_current = False

        new_posting = PostingTransfer(
            staff_id=staff_id,
            station_name=payload["station_name"],
            start_date=transfer_date,
            transfer_reason=payload["transfer_reason"],
            remarks=payload["remarks"],
            is_current=True,
        )
        self.repository.add(new_posting)
        self.session.flush()
        return new_posting

    def _validate_staff_ready(self, raw_staff_id) -> tuple[int, date]:
        try:
            staff_id = int(raw_staff_id)
        except (TypeError, ValueError) as exc:
            raise ValidationError("Staff profile must be selected before posting or transfer.") from exc

        staff = self.staff_repository.get_by_id(staff_id)
        if staff is None:
            raise ValidationError("Staff profile must already exist before posting or transfer.")

        service_record = self.service_record_repository.latest_for_staff(staff_id)
        if service_record is None:
            raise ValidationError("A service record must exist before posting or transfer.")

        return staff_id, service_record.date_first_appointment

    def _validate_posting_payload(
        self,
        data: dict,
        station_field: str,
        date_field: str,
        date_label: str,
        first_appointment_date: date,
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

        if errors:
            raise ValidationError(errors)

        return {
            "station_name": station_name,
            "posting_date": posting_date,
            "transfer_reason": optional_text(data, "transfer_reason"),
            "remarks": optional_text(data, "remarks"),
        }
