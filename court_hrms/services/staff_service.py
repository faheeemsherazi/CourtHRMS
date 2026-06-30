from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from court_hrms.models.staff_profile import StaffProfile
from court_hrms.repositories.staff_repository import StaffRepository
from court_hrms.utils.date_utils import calculate_retirement_date
from court_hrms.utils.validators import (
    ValidationError,
    clean_text,
    optional_text,
    require_text,
    validate_adult_birth_date,
    validate_cnic,
    validate_digits_max_length,
    validate_email,
    validate_exact_digits,
    validate_minimum_length,
)


class StaffService:
    def __init__(self, session: Session):
        self.repository = StaffRepository(session)

    def list_staff(self) -> list[StaffProfile]:
        return self.repository.list_all()

    def count_staff(self) -> int:
        return self.repository.count()

    def get_by_personal_number(self, personal_number: str) -> StaffProfile | None:
        personal_number = (personal_number or "").strip()
        if not personal_number:
            return None
        return self.repository.get_by_personal_number(personal_number)

    def create_staff(self, data: dict) -> StaffProfile:
        payload = self._validate_staff_payload(data)
        staff = StaffProfile(**payload)
        try:
            return self.repository.add(staff)
        except IntegrityError as exc:
            raise ValidationError(
                "Personal number or CNIC already exists. Please verify the staff profile."
            ) from exc

    def update_staff(self, staff_id: int, data: dict) -> StaffProfile:
        staff = self.repository.get_by_id(staff_id)
        if staff is None:
            raise ValidationError("Staff profile was not found.")

        payload = self._validate_staff_payload(data, exclude_staff_id=staff_id)
        for field, value in payload.items():
            setattr(staff, field, value)
        try:
            self.repository.session.flush()
        except IntegrityError as exc:
            raise ValidationError(
                "Personal number or CNIC already exists. Please verify the staff profile."
            ) from exc
        return staff

    def _validate_staff_payload(
        self,
        data: dict,
        exclude_staff_id: int | None = None,
    ) -> dict:
        errors: list[str] = []

        personal_number = require_text(data, "personal_number", "Personal number", errors)
        full_name = require_text(data, "full_name", "Full name", errors)
        father_name = require_text(data, "father_name", "Father name", errors)
        cnic = clean_text(data.get("cnic"))
        validate_cnic(cnic, errors)
        district = require_text(data, "district", "District", errors)
        mobile_number = clean_text(data.get("mobile_number"))
        validate_exact_digits(mobile_number, "Mobile number", 11, errors, required=True)
        present_address = clean_text(data.get("present_address"))
        validate_minimum_length(present_address, "Present address", 5, errors, required=True)
        permanent_address = clean_text(data.get("permanent_address"))
        validate_minimum_length(permanent_address, "Permanent address", 5, errors, required=True)
        emergency_contact = clean_text(data.get("emergency_contact"))
        validate_digits_max_length(emergency_contact, "Emergency contact", 17, errors)

        date_of_birth = validate_adult_birth_date(data.get("date_of_birth"), errors)
        email = optional_text(data, "email")
        validate_email(email, errors)

        if personal_number:
            existing = self.repository.get_by_personal_number(personal_number)
            if existing and existing.id != exclude_staff_id:
                errors.append("Personal number already exists.")

        if cnic:
            existing = self.repository.get_by_cnic(cnic)
            if existing and existing.id != exclude_staff_id:
                errors.append("CNIC already exists.")

        if errors:
            raise ValidationError(errors)

        return {
            "personal_number": personal_number,
            "full_name": full_name,
            "father_name": father_name,
            "cnic": cnic,
            "date_of_birth": date_of_birth,
            "gender": optional_text(data, "gender"),
            "religion": optional_text(data, "religion"),
            "marital_status": optional_text(data, "marital_status"),
            "domicile": optional_text(data, "domicile"),
            "district": district,
            "tehsil": optional_text(data, "tehsil"),
            "mobile_number": mobile_number,
            "email": email,
            "present_address": present_address,
            "permanent_address": permanent_address,
            "emergency_contact": emergency_contact,
            "qualification": optional_text(data, "qualification"),
            "date_of_retirement": calculate_retirement_date(date_of_birth),
        }
