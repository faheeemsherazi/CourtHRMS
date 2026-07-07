from __future__ import annotations

import unittest
from datetime import date, datetime

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from court_hrms.database.db import Base
from court_hrms.models import ServiceRecord, StaffProfile
from court_hrms.services.seniority_service import SeniorityService
from court_hrms.utils.seniority_rules import (
    SeniorityCandidate,
    rank_seniority_candidates,
)


class SeniorityServiceTest(unittest.TestCase):
    def _candidate(
        self,
        personal_number: str,
        appointment: date | None,
        promotion: date | None = None,
        merit: int | None = None,
        birth: date | None = None,
        designation: str = "Junior Clerk",
    ) -> SeniorityCandidate:
        return SeniorityCandidate(
            staff_id=int(personal_number[-2:]),
            personal_number=personal_number,
            full_name=f"Staff {personal_number}",
            father_name="Father Name",
            designation=designation,
            bps=9,
            date_first_appointment=appointment,
            date_current_promotion=promotion,
            selection_merit_number=merit,
            date_of_birth=birth or date(1990, 1, 1),
            current_posting="District Court Orakzai",
        )

    def _rank_numbers(self, candidates: list[SeniorityCandidate]) -> list[str]:
        result = rank_seniority_candidates(
            "Junior Clerk",
            candidates,
            datetime(2026, 1, 1, 10, 0, 0),
        )
        return [row.personal_number for row in result.ranked]

    def test_earlier_appointment_ranks_higher(self) -> None:
        order = self._rank_numbers(
            [
                self._candidate("PN-02", date(2015, 1, 1)),
                self._candidate("PN-01", date(2010, 1, 1)),
            ]
        )

        self.assertEqual(order, ["PN-01", "PN-02"])

    def test_appointment_tie_resolved_by_promotion_date(self) -> None:
        order = self._rank_numbers(
            [
                self._candidate("PN-02", date(2010, 1, 1), date(2020, 1, 1)),
                self._candidate("PN-01", date(2010, 1, 1), date(2018, 1, 1)),
            ]
        )

        self.assertEqual(order, ["PN-01", "PN-02"])

    def test_promotion_tie_resolved_by_merit_number(self) -> None:
        order = self._rank_numbers(
            [
                self._candidate("PN-02", date(2010, 1, 1), date(2018, 1, 1), 4),
                self._candidate("PN-01", date(2010, 1, 1), date(2018, 1, 1), 2),
            ]
        )

        self.assertEqual(order, ["PN-01", "PN-02"])

    def test_lower_merit_number_ranks_higher(self) -> None:
        order = self._rank_numbers(
            [
                self._candidate("PN-02", date(2010, 1, 1), merit=10),
                self._candidate("PN-01", date(2010, 1, 1), merit=1),
            ]
        )

        self.assertEqual(order, ["PN-01", "PN-02"])

    def test_merit_tie_resolved_by_age(self) -> None:
        order = self._rank_numbers(
            [
                self._candidate(
                    "PN-02", date(2010, 1, 1), merit=1, birth=date(1990, 1, 1)
                ),
                self._candidate(
                    "PN-01", date(2010, 1, 1), merit=1, birth=date(1980, 1, 1)
                ),
            ]
        )

        self.assertEqual(order, ["PN-01", "PN-02"])

    def test_older_employee_ranks_higher(self) -> None:
        order = self._rank_numbers(
            [
                self._candidate("PN-02", date(2010, 1, 1), birth=date(1985, 1, 1)),
                self._candidate("PN-01", date(2010, 1, 1), birth=date(1975, 1, 1)),
            ]
        )

        self.assertEqual(order, ["PN-01", "PN-02"])

    def test_complete_tie_resolved_by_personal_number(self) -> None:
        order = self._rank_numbers(
            [
                self._candidate("PN-02", date(2010, 1, 1), merit=1),
                self._candidate("PN-01", date(2010, 1, 1), merit=1),
            ]
        )

        self.assertEqual(order, ["PN-01", "PN-02"])

    def test_missing_promotion_sorts_after_valid_promotion(self) -> None:
        order = self._rank_numbers(
            [
                self._candidate("PN-02", date(2010, 1, 1), None),
                self._candidate("PN-01", date(2010, 1, 1), date(2019, 1, 1)),
            ]
        )

        self.assertEqual(order, ["PN-01", "PN-02"])

    def test_missing_merit_sorts_after_valid_merit(self) -> None:
        order = self._rank_numbers(
            [
                self._candidate("PN-02", date(2010, 1, 1), merit=None),
                self._candidate("PN-01", date(2010, 1, 1), merit=5),
            ]
        )

        self.assertEqual(order, ["PN-01", "PN-02"])

    def test_missing_first_appointment_is_excluded(self) -> None:
        result = rank_seniority_candidates(
            "Junior Clerk",
            [
                self._candidate("PN-01", None),
                self._candidate("PN-02", date(2010, 1, 1)),
            ],
            datetime(2026, 1, 1, 10, 0, 0),
        )

        self.assertEqual([row.personal_number for row in result.ranked], ["PN-02"])
        self.assertEqual(result.excluded[0].personal_number, "PN-01")
        self.assertEqual(result.excluded[0].missing_field, "Date of First Appointment")

    def test_generated_ranks_start_at_one_with_no_gaps(self) -> None:
        result = rank_seniority_candidates(
            "Junior Clerk",
            [
                self._candidate("PN-03", date(2012, 1, 1)),
                self._candidate("PN-01", date(2010, 1, 1)),
                self._candidate("PN-02", date(2011, 1, 1)),
            ],
            datetime(2026, 1, 1, 10, 0, 0),
        )

        self.assertEqual([row.rank for row in result.ranked], [1, 2, 3])

    def test_repeated_execution_produces_identical_order(self) -> None:
        candidates = [
            self._candidate("PN-03", date(2012, 1, 1)),
            self._candidate("PN-01", date(2010, 1, 1)),
            self._candidate("PN-02", date(2011, 1, 1)),
        ]

        self.assertEqual(self._rank_numbers(candidates), self._rank_numbers(candidates))

    def test_official_register_fields_are_preserved(self) -> None:
        result = rank_seniority_candidates(
            "Junior Clerk",
            [
                SeniorityCandidate(
                    staff_id=1,
                    personal_number="PN-01",
                    full_name="Syed Muhammad Abdullah Shah Long Official Name",
                    father_name="Father Name",
                    designation="Junior Clerk",
                    bps=9,
                    date_first_appointment=date(2010, 1, 1),
                    date_current_promotion=date(2020, 1, 1),
                    selection_merit_number=1,
                    date_of_birth=date(1980, 1, 1),
                    current_posting="District Court Orakzai",
                    qualification="BA",
                    first_government_entry=date(2009, 1, 1),
                    first_judiciary_entry=date(2010, 1, 1),
                    current_post_date=date(2022, 1, 1),
                    retirement_date=date(2040, 1, 1),
                    remarks="No remarks",
                )
            ],
            datetime(2026, 1, 1, 10, 0, 0),
        )

        row = result.ranked[0].to_dict()

        self.assertEqual(
            row["full_name"], "Syed Muhammad Abdullah Shah Long Official Name"
        )
        self.assertEqual(row["qualification"], "BA")
        self.assertEqual(row["first_government_entry"], date(2009, 1, 1))
        self.assertEqual(row["first_judiciary_entry"], date(2010, 1, 1))
        self.assertEqual(row["current_post_date"], date(2022, 1, 1))
        self.assertEqual(row["promotion_date"], date(2020, 1, 1))
        self.assertEqual(row["retirement_date"], date(2040, 1, 1))
        self.assertEqual(row["remarks"], "No remarks")


class SeniorityRepositoryFilteringTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:", future=True)

        @event.listens_for(self.engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        Base.metadata.create_all(self.engine)
        session_factory = sessionmaker(
            bind=self.engine, expire_on_commit=False, future=True
        )
        self.session = session_factory()
        self.service = SeniorityService(self.session)

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def _add_staff(
        self,
        personal_number: str,
        designation: str,
        status: str = "Active",
        appointment: date = date(2010, 1, 1),
    ) -> None:
        staff = StaffProfile(
            personal_number=personal_number,
            full_name=f"Staff {personal_number}",
            father_name="Father Name",
            cnic=f"17301123{personal_number[-4:]}",
            date_of_birth=date(1980, 1, 1),
            district="Orakzai",
            mobile_number="03001234567",
            present_address="District Court Orakzai",
            permanent_address="District Orakzai",
        )
        self.session.add(staff)
        self.session.flush()
        self.session.add(
            ServiceRecord(
                staff_id=staff.id,
                designation=designation,
                bps=9,
                employment_type="Permanent",
                employment_status=status,
                date_first_appointment=appointment,
            )
        )
        self.session.flush()

    def test_inactive_employees_are_excluded(self) -> None:
        self._add_staff("PN-0001", "Junior Clerk", "Active")
        self._add_staff("PN-0002", "Junior Clerk", "Retired")

        result = self.service.generate_seniority_list("Junior Clerk")

        self.assertEqual([row.personal_number for row in result.ranked], ["PN-0001"])

    def test_different_designations_are_not_mixed(self) -> None:
        self._add_staff("PN-0001", "Junior Clerk", "Active")
        self._add_staff("PN-0002", "Stenographer", "Active")

        result = self.service.generate_seniority_list("Junior Clerk")

        self.assertEqual([row.personal_number for row in result.ranked], ["PN-0001"])


if __name__ == "__main__":
    unittest.main()
