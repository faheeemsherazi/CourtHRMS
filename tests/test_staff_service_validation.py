from __future__ import annotations

import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from court_hrms.database.db import Base
from court_hrms.models.admin import Admin
from court_hrms.models.posting_transfer import PostingTransfer
from court_hrms.models.service_record import ServiceRecord
from court_hrms.models.staff_profile import StaffProfile
from court_hrms.services.staff_service import StaffService
from court_hrms.utils.validators import ValidationError


def valid_staff_data(**overrides) -> dict:
    data = {
        "personal_number": "DC-ORZ-0001",
        "full_name": "Muhammad Ali Khan",
        "father_name": "Abdul Karim Khan",
        "cnic": "1730112345671",
        "date_of_birth": date(1990, 5, 20),
        "gender": "Male",
        "religion": "Islam",
        "marital_status": "Married",
        "domicile": "Orakzai",
        "district": "Orakzai",
        "tehsil": "Lower Orakzai",
        "mobile_number": "03001234567",
        "email": "ali.khan@example.com",
        "present_address": "District Courts Orakzai",
        "permanent_address": "Village Samana, District Orakzai",
        "emergency_contact": "03017654321",
        "qualification": "BA",
    }
    data.update(overrides)
    return data


class StaffServiceValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        _ = (Admin, PostingTransfer, ServiceRecord, StaffProfile)
        self.engine = create_engine("sqlite:///:memory:", future=True)
        Base.metadata.create_all(self.engine)
        session_factory = sessionmaker(bind=self.engine, future=True)
        self.session = session_factory()
        self.service = StaffService(self.session)

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def assert_validation_messages(self, data: dict, *expected_messages: str) -> None:
        with self.assertRaises(ValidationError) as context:
            self.service.create_staff(data)

        messages = context.exception.messages
        for expected in expected_messages:
            self.assertIn(expected, messages)

    def test_valid_profile_accepts_optional_tehsil_and_short_emergency_contact(
        self,
    ) -> None:
        staff = self.service.create_staff(
            valid_staff_data(
                tehsil="",
                emergency_contact="1155",
            )
        )

        self.assertEqual(staff.mobile_number, "03001234567")
        self.assertEqual(staff.district, "Orakzai")
        self.assertIsNone(staff.tehsil)
        self.assertEqual(staff.emergency_contact, "1155")

    def test_valid_profile_accepts_seventeen_digit_emergency_contact(self) -> None:
        staff = self.service.create_staff(
            valid_staff_data(
                emergency_contact="1" * 17,
            )
        )

        self.assertEqual(staff.emergency_contact, "1" * 17)

    def test_optional_profile_fields_can_remain_blank(self) -> None:
        staff = self.service.create_staff(
            valid_staff_data(
                gender="",
                religion="",
                marital_status="",
                domicile="",
                tehsil="",
                email="",
                emergency_contact="",
                qualification="",
            )
        )

        self.assertIsNone(staff.gender)
        self.assertIsNone(staff.religion)
        self.assertIsNone(staff.marital_status)
        self.assertIsNone(staff.domicile)
        self.assertIsNone(staff.tehsil)
        self.assertIsNone(staff.email)
        self.assertIsNone(staff.emergency_contact)
        self.assertIsNone(staff.qualification)

    def test_mobile_number_must_be_exactly_eleven_digits(self) -> None:
        invalid_numbers = ["0300123456", "030012345678", "0300ABC4567", ""]

        for mobile_number in invalid_numbers:
            with self.subTest(mobile_number=mobile_number):
                expected = (
                    "Mobile number is required."
                    if mobile_number == ""
                    else "Mobile number must be exactly 11 digits."
                )
                self.assert_validation_messages(
                    valid_staff_data(mobile_number=mobile_number),
                    expected,
                )

    def test_emergency_contact_must_be_digits_and_no_more_than_seventeen_digits(
        self,
    ) -> None:
        self.assert_validation_messages(
            valid_staff_data(emergency_contact="0300ABC4567"),
            "Emergency contact must contain digits only.",
        )
        self.assert_validation_messages(
            valid_staff_data(emergency_contact="1" * 18),
            "Emergency contact cannot be more than 17 digits.",
        )

    def test_district_required_and_addresses_must_be_at_least_five_characters(
        self,
    ) -> None:
        self.assert_validation_messages(
            valid_staff_data(
                district="",
                present_address="ABCD",
                permanent_address="WXYZ",
            ),
            "District is required.",
            "Present address must be at least 5 characters.",
            "Permanent address must be at least 5 characters.",
        )

        self.assert_validation_messages(
            valid_staff_data(
                present_address="",
                permanent_address="",
            ),
            "Present address is required.",
            "Permanent address is required.",
        )

    def test_names_locations_and_addresses_must_include_letters(self) -> None:
        self.assert_validation_messages(
            valid_staff_data(
                full_name="123",
                father_name="456",
                district="789",
                tehsil="101",
                present_address="12345",
                permanent_address="67890",
            ),
            "Full name must include letters, not numbers only.",
            "Father name must include letters, not numbers only.",
            "District must include letters, not numbers only.",
            "Tehsil must include letters, not numbers only.",
            "Present address must include letters, not numbers only.",
            "Permanent address must include letters, not numbers only.",
        )

    def test_names_and_locations_must_meet_minimum_lengths(self) -> None:
        self.assert_validation_messages(
            valid_staff_data(
                full_name="M",
                father_name="A",
                district="Or",
                tehsil="Up",
            ),
            "Full name must be at least 3 characters.",
            "Father name must be at least 3 characters.",
            "District must be at least 3 characters.",
            "Tehsil must be at least 3 characters.",
        )

    def test_addresses_accept_letters_and_numbers_together(self) -> None:
        staff = self.service.create_staff(
            valid_staff_data(
                district="District 12",
                tehsil="Tehsil 2",
                present_address="House 12, Court Road",
                permanent_address="Street 4, Orakzai",
            )
        )

        self.assertEqual(staff.district, "District 12")
        self.assertEqual(staff.tehsil, "Tehsil 2")
        self.assertEqual(staff.present_address, "House 12, Court Road")
        self.assertEqual(staff.permanent_address, "Street 4, Orakzai")

    def test_date_of_birth_must_show_employee_is_adult(self) -> None:
        self.assert_validation_messages(
            valid_staff_data(date_of_birth=date(2010, 1, 1)),
            "Date of birth must show the employee is at least 18 years old.",
        )

    def test_cnic_must_be_exactly_thirteen_digits(self) -> None:
        for cnic in ["173011234567", "17301123456712", "17301ABC45671", ""]:
            with self.subTest(cnic=cnic):
                expected = (
                    "CNIC is required."
                    if cnic == ""
                    else "CNIC must be exactly 13 digits without dashes."
                )
                self.assert_validation_messages(valid_staff_data(cnic=cnic), expected)

    def test_invalid_email_is_rejected(self) -> None:
        self.assert_validation_messages(
            valid_staff_data(email="not-an-email"),
            "Email address is not valid.",
        )

    def test_required_identity_fields_are_rejected_when_missing(self) -> None:
        self.assert_validation_messages(
            valid_staff_data(
                personal_number="",
                full_name="",
                father_name="",
            ),
            "Personal number is required.",
            "Full name is required.",
            "Father name is required.",
        )

    def test_duplicate_personal_number_and_cnic_are_rejected(self) -> None:
        self.service.create_staff(valid_staff_data())

        self.assert_validation_messages(
            valid_staff_data(
                full_name="Sanaullah Khan",
                mobile_number="03111234567",
                emergency_contact="03117654321",
            ),
            "Personal number already exists.",
            "CNIC already exists.",
        )

    def test_update_allows_same_identifiers_and_revalidates_changed_fields(
        self,
    ) -> None:
        staff = self.service.create_staff(valid_staff_data())

        updated = self.service.update_staff(
            staff.id,
            valid_staff_data(
                full_name="Muhammad Ali Khan Updated",
                present_address="Civil Courts Orakzai",
            ),
        )
        self.assertEqual(updated.full_name, "Muhammad Ali Khan Updated")
        self.assertEqual(updated.personal_number, "DC-ORZ-0001")
        self.assertEqual(updated.cnic, "1730112345671")

        with self.assertRaises(ValidationError) as context:
            self.service.update_staff(
                staff.id,
                valid_staff_data(mobile_number="12345"),
            )
        self.assertIn(
            "Mobile number must be exactly 11 digits.", context.exception.messages
        )


if __name__ == "__main__":
    unittest.main()
