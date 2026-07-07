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
from court_hrms.services.posting_service import PostingService
from court_hrms.utils.validators import ValidationError


class PostingServiceValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        _ = (Admin, PostingTransfer, ServiceRecord, StaffProfile)
        self.engine = create_engine("sqlite:///:memory:", future=True)
        Base.metadata.create_all(self.engine)
        session_factory = sessionmaker(bind=self.engine, future=True)
        self.session = session_factory()
        self.service = PostingService(self.session)

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def create_staff_with_service_record(self) -> StaffProfile:
        staff = StaffProfile(
            personal_number="DC-ORZ-0002",
            full_name="Sanaullah Khan",
            father_name="Rahimullah Khan",
            cnic="1730123456782",
            date_of_birth=date(1986, 11, 4),
            district="Orakzai",
            mobile_number="03111234567",
            present_address="Sessions Court Hangu Road",
            permanent_address="Kurez, District Orakzai",
        )
        self.session.add(staff)
        self.session.flush()

        service_record = ServiceRecord(
            staff_id=staff.id,
            designation="Stenographer",
            bps=15,
            employment_type="Permanent",
            employment_status="Active",
            date_first_appointment=date(2011, 3, 10),
        )
        self.session.add(service_record)
        self.session.flush()
        return staff

    def test_transfer_without_first_posting_is_rejected(self) -> None:
        staff = self.create_staff_with_service_record()

        with self.assertRaises(ValidationError) as context:
            self.service.execute_transfer(
                {
                    "staff_id": staff.id,
                    "new_station": "District Court Record Branch",
                    "transfer_date": date(2019, 8, 1),
                    "transfer_reason": "Record branch workload adjustment.",
                }
            )

        self.assertIn(
            "No current posting was found. Add the first posting before transfer.",
            context.exception.messages,
        )

    def test_transfer_after_first_posting_closes_current_and_adds_new_current(
        self,
    ) -> None:
        staff = self.create_staff_with_service_record()

        first_posting = self.service.add_first_posting(
            {
                "staff_id": staff.id,
                "station_name": "Civil Court Hangu Camp",
                "start_date": date(2011, 3, 10),
                "transfer_reason": "Initial posting.",
            }
        )

        new_posting = self.service.execute_transfer(
            {
                "staff_id": staff.id,
                "new_station": "District Court Record Branch",
                "transfer_date": date(2019, 8, 1),
                "transfer_reason": "Record branch workload adjustment.",
            }
        )

        self.assertFalse(first_posting.is_current)
        self.assertEqual(first_posting.end_date, date(2019, 8, 1))
        self.assertTrue(new_posting.is_current)
        self.assertEqual(new_posting.station_name, "District Court Record Branch")

    def test_transfer_populates_official_movement_fields(self) -> None:
        staff = self.create_staff_with_service_record()
        self.service.add_first_posting(
            {
                "staff_id": staff.id,
                "station_name": "Civil Court Hangu Camp",
                "start_date": date(2011, 3, 10),
            }
        )

        posting = self.service.execute_transfer(
            {
                "staff_id": staff.id,
                "new_station": "District Court Record Branch",
                "transfer_date": date(2019, 8, 1),
                "order_number": "DC/Transfer/15",
                "order_date": date(2019, 7, 25),
                "issuing_authority": "District & Sessions Judge, Orakzai",
                "relieving_date": date(2019, 8, 1),
                "joining_date": date(2019, 8, 1),
                "charge_assumed_date": date(2019, 8, 1),
                "transfer_category": "Administrative",
                "status": "Completed",
            }
        )

        self.assertEqual(posting.movement_type, "Transfer")
        self.assertEqual(posting.from_station, "Civil Court Hangu Camp")
        self.assertEqual(posting.to_station, "District Court Record Branch")
        self.assertEqual(posting.order_number, "DC/Transfer/15")
        self.assertEqual(
            posting.issuing_authority, "District & Sessions Judge, Orakzai"
        )
        self.assertEqual(posting.relieving_date, date(2019, 8, 1))
        self.assertEqual(posting.joining_date, date(2019, 8, 1))

    def test_joining_date_before_relieving_date_is_rejected(self) -> None:
        staff = self.create_staff_with_service_record()
        self.service.add_first_posting(
            {
                "staff_id": staff.id,
                "station_name": "Civil Court Hangu Camp",
                "start_date": date(2011, 3, 10),
            }
        )

        with self.assertRaises(ValidationError) as context:
            self.service.execute_transfer(
                {
                    "staff_id": staff.id,
                    "new_station": "District Court Record Branch",
                    "transfer_date": date(2019, 8, 1),
                    "relieving_date": date(2019, 8, 5),
                    "joining_date": date(2019, 8, 1),
                }
            )

        self.assertIn(
            "Joining date cannot be before relieving date.",
            context.exception.messages,
        )

    def test_duplicate_order_reference_requires_audit_reason(self) -> None:
        first_staff = self.create_staff_with_service_record()
        self.service.add_first_posting(
            {
                "staff_id": first_staff.id,
                "station_name": "Civil Court Hangu Camp",
                "start_date": date(2011, 3, 10),
                "order_number": "DC/Post/1",
                "order_date": date(2011, 3, 10),
                "issuing_authority": "District & Sessions Judge, Orakzai",
            }
        )

        second_staff = StaffProfile(
            personal_number="DC-ORZ-0003",
            full_name="Muhammad Iqbal",
            father_name="Khalid Khan",
            cnic="1730123456783",
            date_of_birth=date(1989, 1, 1),
            district="Orakzai",
            mobile_number="03111234568",
            present_address="Sessions Court Hangu Road",
            permanent_address="Kurez, District Orakzai",
        )
        self.session.add(second_staff)
        self.session.flush()
        self.session.add(
            ServiceRecord(
                staff_id=second_staff.id,
                designation="Stenographer",
                bps=15,
                employment_type="Permanent",
                employment_status="Active",
                date_first_appointment=date(2012, 1, 1),
            )
        )
        self.session.flush()

        with self.assertRaises(ValidationError) as context:
            self.service.add_first_posting(
                {
                    "staff_id": second_staff.id,
                    "station_name": "District Court Record Branch",
                    "start_date": date(2012, 1, 1),
                    "order_number": "DC/Post/1",
                    "order_date": date(2011, 3, 15),
                    "issuing_authority": "District & Sessions Judge, Orakzai",
                }
            )

        self.assertIn(
            "Order number already exists for this issuing authority and year. "
            "Provide an audit reason to override.",
            context.exception.messages,
        )


if __name__ == "__main__":
    unittest.main()
