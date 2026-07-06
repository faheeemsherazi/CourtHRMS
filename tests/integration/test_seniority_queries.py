from __future__ import annotations

import unittest
from datetime import date

from court_hrms.services.seniority_service import SeniorityService
from tests.integration.helpers import add_service_record, add_staff, create_test_session


class SeniorityQueryIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine, self.session = create_test_session()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_seniority_query_filters_and_orders_active_designation(self) -> None:
        senior = add_staff(self.session, "PN-2001", "Senior Staff", date(1975, 1, 1))
        junior = add_staff(self.session, "PN-2002", "Junior Staff", date(1980, 1, 1))
        inactive = add_staff(
            self.session, "PN-2003", "Inactive Staff", date(1970, 1, 1)
        )
        other = add_staff(self.session, "PN-2004", "Other Staff", date(1965, 1, 1))
        add_service_record(self.session, senior.id, "Junior Clerk", date(2010, 1, 1))
        add_service_record(self.session, junior.id, "Junior Clerk", date(2012, 1, 1))
        add_service_record(
            self.session, inactive.id, "Junior Clerk", date(2000, 1, 1), "Retired"
        )
        add_service_record(self.session, other.id, "Stenographer", date(1999, 1, 1))

        result = SeniorityService(self.session).generate_seniority_list("Junior Clerk")

        self.assertEqual(
            [row.personal_number for row in result.ranked],
            ["PN-2001", "PN-2002"],
        )


if __name__ == "__main__":
    unittest.main()
