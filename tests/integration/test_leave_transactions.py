from __future__ import annotations

import unittest
from datetime import date

from sqlalchemy import func, select

from court_hrms.models import AnnualLeaveAccount, LeaveRecord
from court_hrms.services.leave_service import LeaveService
from court_hrms.utils.exceptions import LeaveBalanceError
from tests.integration.helpers import add_admin, add_staff, create_test_session


class LeaveTransactionIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine, self.session = create_test_session()
        self.admin = add_admin(self.session)
        self.staff = add_staff(self.session, "PN-1001")
        self.service = LeaveService(self.session)

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_successful_leave_updates_balance_and_history_atomically(self) -> None:
        result = self.service.process_leave(
            {
                "staff_id": self.staff.id,
                "leave_year": 2026,
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 1, 5),
                "reason": "Personal work",
                "processed_by_admin_id": self.admin.id,
            }
        )

        self.assertEqual(result["summary"]["remaining_days"], 20)
        self.assertEqual(
            self.session.execute(select(func.count(LeaveRecord.id))).scalar_one(),
            1,
        )

    def test_failed_leave_does_not_insert_history_or_change_balance(self) -> None:
        self.service.process_leave(
            {
                "staff_id": self.staff.id,
                "leave_year": 2026,
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 1, 5),
                "reason": "Personal work",
                "processed_by_admin_id": self.admin.id,
            }
        )

        with self.assertRaises(LeaveBalanceError):
            self.service.process_leave(
                {
                    "staff_id": self.staff.id,
                    "leave_year": 2026,
                    "start_date": date(2026, 2, 1),
                    "end_date": date(2026, 2, 21),
                    "reason": "Long leave",
                    "processed_by_admin_id": self.admin.id,
                }
            )

        account = self.session.execute(select(AnnualLeaveAccount)).scalar_one()
        self.assertEqual(account.availed_days, 5)
        self.assertEqual(account.remaining_days, 20)
        self.assertEqual(
            self.session.execute(select(func.count(LeaveRecord.id))).scalar_one(),
            1,
        )


if __name__ == "__main__":
    unittest.main()
