from __future__ import annotations

import unittest
from datetime import date

from court_hrms.repositories.seniority_workflow_repository import (
    SeniorityWorkflowRepository,
)
from court_hrms.services.seniority_workflow_service import SeniorityWorkflowService
from court_hrms.utils.exceptions import SeniorityDataError
from tests.integration.helpers import add_service_record, add_staff, create_test_session


class SeniorityWorkflowServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine, self.session = create_test_session()
        self.service = SeniorityWorkflowService(self.session)

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def _seed_staff(self) -> None:
        senior = add_staff(
            self.session,
            "PN-3001",
            "Syed Muhammad Abdullah Shah Long Official Name",
            date(1975, 1, 1),
        )
        senior.qualification = "MA"
        senior.date_of_joining_government_service = date(2009, 1, 1)
        senior.date_of_joining_district_judiciary = date(2010, 1, 1)
        senior.date_of_retirement = date(2035, 1, 1)
        junior = add_staff(
            self.session,
            "PN-3002",
            "Junior Staff",
            date(1985, 1, 1),
        )
        add_service_record(self.session, senior.id, "Junior Clerk", date(2010, 1, 1))
        add_service_record(self.session, junior.id, "Junior Clerk", date(2012, 1, 1))

    def test_draft_snapshot_is_immutable_after_live_data_changes(self) -> None:
        self._seed_staff()
        seniority_list = self.service.create_snapshot(
            designation="Junior Clerk",
            list_year=2026,
            list_type="Draft",
        )
        self.session.commit()

        staff = add_staff(
            self.session,
            "PN-3003",
            "Newer Live Staff",
            date(1990, 1, 1),
        )
        add_service_record(self.session, staff.id, "Junior Clerk", date(2000, 1, 1))
        self.session.commit()

        entries = SeniorityWorkflowRepository(self.session).list_entries(
            seniority_list.id
        )

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].personal_number, "PN-3001")
        self.assertEqual(
            entries[0].full_name,
            "Syed Muhammad Abdullah Shah Long Official Name",
        )
        self.assertEqual(entries[0].qualification, "MA")
        self.assertEqual(entries[0].first_government_entry, date(2009, 1, 1))
        self.assertEqual(entries[0].first_judiciary_entry, date(2010, 1, 1))
        self.assertEqual(entries[0].retirement_date, date(2035, 1, 1))

    def test_repeated_snapshot_increments_version(self) -> None:
        self._seed_staff()

        first = self.service.create_snapshot(
            designation="Junior Clerk",
            list_year=2026,
            list_type="Draft",
        )
        second = self.service.create_snapshot(
            designation="Junior Clerk",
            list_year=2026,
            list_type="Draft",
        )

        self.assertEqual(first.version_number, 1)
        self.assertEqual(second.version_number, 2)

    def test_finalized_list_rejects_new_objections(self) -> None:
        self._seed_staff()
        seniority_list = self.service.create_snapshot(
            designation="Junior Clerk",
            list_year=2026,
            list_type="Draft",
        )
        self.service.finalize_list(seniority_list.id)

        with self.assertRaises(SeniorityDataError):
            self.service.create_objection(
                seniority_list_id=seniority_list.id,
                objection_number="OBJ-1",
                staff_id=1,
                submitted_date=date(2026, 7, 1),
                subject="Rank objection",
                details="Request review.",
            )


if __name__ == "__main__":
    unittest.main()
