from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import patch

from sqlalchemy import create_engine, event, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from court_hrms.database.db import Base
from court_hrms.models import (
    Admin,
    AnnualLeaveAccount,
    LeaveRecord,
    StaffProfile,
)
from court_hrms.services.leave_service import LeaveService
from court_hrms.utils.exceptions import (
    AuthenticationRequiredError,
    DatabaseOperationError,
    LeaveBalanceError,
    LeaveDateError,
    StaffNotFoundError,
)


class LeaveServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:", future=True)

        @event.listens_for(self.engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        Base.metadata.create_all(self.engine)
        session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            future=True,
        )
        self.session = session_factory()
        self.admin = Admin(
            username="admin",
            password_hash="not-used",
            full_name="System Administrator",
        )
        self.staff = StaffProfile(
            personal_number="DC-ORZ-0100",
            full_name="Muhammad Imran Khan",
            father_name="Abdul Karim Khan",
            cnic="1730112345600",
            date_of_birth=date(1985, 4, 15),
            district="Orakzai",
            mobile_number="03001234000",
            present_address="District Court Orakzai",
            permanent_address="District Orakzai",
        )
        self.session.add_all([self.admin, self.staff])
        self.session.flush()
        self.service = LeaveService(self.session)

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def _leave_payload(self, **overrides) -> dict:
        payload = {
            "staff_id": self.staff.id,
            "leave_year": 2026,
            "start_date": date(2026, 1, 1),
            "end_date": date(2026, 1, 1),
            "reason": "Personal work",
            "remarks": "",
            "processed_by_admin_id": self.admin.id,
        }
        payload.update(overrides)
        return payload

    def _account(self) -> AnnualLeaveAccount:
        account = self.session.execute(select(AnnualLeaveAccount)).scalar_one()
        return account

    def _record_count(self) -> int:
        return int(
            self.session.execute(select(func.count(LeaveRecord.id))).scalar_one()
        )

    def test_new_staff_year_account_defaults_to_25_days(self) -> None:
        summary = self.service.get_account_summary(self.staff.id, 2026)

        self.assertEqual(summary["entitlement_days"], 25)
        self.assertEqual(summary["availed_days"], 0)
        self.assertEqual(summary["remaining_days"], 25)

    def test_one_day_leave_leaves_24_days(self) -> None:
        result = self.service.process_leave(self._leave_payload())

        self.assertEqual(result["summary"]["availed_days"], 1)
        self.assertEqual(result["summary"]["remaining_days"], 24)
        self.assertEqual(self._record_count(), 1)

    def test_exactly_25_days_is_accepted(self) -> None:
        result = self.service.process_leave(
            self._leave_payload(end_date=date(2026, 1, 25))
        )

        self.assertEqual(result["summary"]["availed_days"], 25)
        self.assertEqual(result["summary"]["remaining_days"], 0)

    def test_twenty_six_days_is_rejected(self) -> None:
        with self.assertRaises(LeaveBalanceError):
            self.service.process_leave(self._leave_payload(end_date=date(2026, 1, 26)))

        self.assertEqual(self._record_count(), 0)

    def test_request_exceeding_remaining_balance_is_rejected(self) -> None:
        self.service.process_leave(self._leave_payload(end_date=date(2026, 1, 20)))

        with self.assertRaises(LeaveBalanceError):
            self.service.process_leave(
                self._leave_payload(
                    start_date=date(2026, 2, 1), end_date=date(2026, 2, 10)
                )
            )

        account = self._account()
        self.assertEqual(account.availed_days, 20)
        self.assertEqual(account.remaining_days, 5)
        self.assertEqual(self._record_count(), 1)

    def test_end_date_before_start_date_is_rejected(self) -> None:
        with self.assertRaises(LeaveDateError):
            self.service.process_leave(
                self._leave_payload(
                    start_date=date(2026, 1, 3), end_date=date(2026, 1, 2)
                )
            )

    def test_same_day_leave_counts_as_one_day(self) -> None:
        days = self.service.calculate_requested_days(date(2026, 6, 1), date(2026, 6, 1))

        self.assertEqual(days, 1)

    def test_cross_year_leave_is_rejected(self) -> None:
        with self.assertRaises(LeaveDateError) as context:
            self.service.process_leave(
                self._leave_payload(
                    start_date=date(2026, 12, 31), end_date=date(2027, 1, 1)
                )
            )

        self.assertIn(
            "A leave request cannot cross calendar years. Record each year separately.",
            context.exception.messages,
        )

    def test_failed_insert_rolls_back_balance_update(self) -> None:
        with patch.object(
            self.service.repository,
            "add_record",
            side_effect=SQLAlchemyError("insert failed"),
        ):
            with self.assertRaises(DatabaseOperationError):
                self.service.process_leave(self._leave_payload())

        self.assertEqual(self._record_count(), 0)
        self.assertEqual(
            self.session.execute(
                select(func.count(AnnualLeaveAccount.id))
            ).scalar_one(),
            0,
        )

    def test_failed_balance_update_rolls_back_history_insert(self) -> None:
        self.session.add(
            AnnualLeaveAccount(
                staff_id=self.staff.id,
                leave_year=2026,
                entitlement_days=25,
                availed_days=0,
            )
        )
        self.session.flush()
        self.session.commit()

        def add_without_flush(record: LeaveRecord) -> LeaveRecord:
            self.session.add(record)
            return record

        with patch.object(
            self.service.repository, "add_record", side_effect=add_without_flush
        ):
            with patch.object(
                self.session, "flush", side_effect=SQLAlchemyError("flush failed")
            ):
                with self.assertRaises(DatabaseOperationError):
                    self.service.process_leave(self._leave_payload())

        account = self._account()
        self.assertEqual(account.availed_days, 0)
        self.assertEqual(self._record_count(), 0)

    def test_duplicate_annual_accounts_are_prevented(self) -> None:
        self.session.add_all(
            [
                AnnualLeaveAccount(staff_id=self.staff.id, leave_year=2026),
                AnnualLeaveAccount(staff_id=self.staff.id, leave_year=2026),
            ]
        )

        with self.assertRaises(IntegrityError):
            self.session.flush()

    def test_remaining_balance_never_becomes_negative(self) -> None:
        self.service.process_leave(self._leave_payload(end_date=date(2026, 1, 25)))

        with self.assertRaises(LeaveBalanceError):
            self.service.process_leave(
                self._leave_payload(
                    start_date=date(2026, 2, 1), end_date=date(2026, 2, 1)
                )
            )

        account = self._account()
        self.assertEqual(account.remaining_days, 0)
        self.assertEqual(account.availed_days, 25)

    def test_nonexistent_staff_is_rejected(self) -> None:
        with self.assertRaises(StaffNotFoundError):
            self.service.process_leave(self._leave_payload(staff_id=9999))

    def test_missing_authenticated_session_is_rejected(self) -> None:
        with self.assertRaises(AuthenticationRequiredError):
            self.service.process_leave(self._leave_payload(processed_by_admin_id=None))

    def test_existing_year_history_loads_correctly(self) -> None:
        self.service.process_leave(
            self._leave_payload(start_date=date(2026, 5, 1), end_date=date(2026, 5, 3))
        )
        self.service.process_leave(
            self._leave_payload(
                leave_year=2027,
                start_date=date(2027, 6, 1),
                end_date=date(2027, 6, 2),
            )
        )

        history_2026 = self.service.list_history(self.staff.id, 2026)

        self.assertEqual(len(history_2026), 1)
        self.assertEqual(history_2026[0]["leave_year"], 2026)
        self.assertEqual(history_2026[0]["days_availed"], 3)


if __name__ == "__main__":
    unittest.main()
