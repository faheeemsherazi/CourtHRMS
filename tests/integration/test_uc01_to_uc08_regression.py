from __future__ import annotations

import os
import unittest
from datetime import date

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import bcrypt
from PySide6.QtWidgets import QApplication
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from court_hrms.controllers.session_controller import SessionController
from court_hrms.models import Admin, PostingTransfer, StaffProfile
from court_hrms.presentation.main_window import MainWindow
from court_hrms.services.auth_service import AuthService
from court_hrms.services.leave_service import LeaveService
from court_hrms.services.posting_service import PostingService
from court_hrms.services.report_service import ReportService
from court_hrms.services.seniority_service import SeniorityService
from court_hrms.services.service_record_service import ServiceRecordService
from court_hrms.services.staff_service import StaffService
from tests.integration.helpers import create_test_session


class UC01ToUC08RegressionIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.engine, self.session = create_test_session()
        self.session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            future=True,
        )
        password_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode("utf-8")
        self.admin = Admin(
            username="admin",
            password_hash=password_hash,
            full_name="System Admin",
        )
        self.session.add(self.admin)
        self.session.flush()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def _staff_payload(self) -> dict:
        return {
            "personal_number": "PN-4001",
            "full_name": "Muhammad Ali Khan",
            "father_name": "Abdul Karim Khan",
            "cnic": "1730112344001",
            "date_of_birth": date(1980, 1, 1),
            "district": "Orakzai",
            "mobile_number": "03001234567",
            "present_address": "District Court Orakzai",
            "permanent_address": "District Orakzai",
        }

    def test_uc01_to_uc08_core_services_remain_working(self) -> None:
        self.assertIsNotNone(
            AuthService(self.session).authenticate("admin", "admin123")
        )

        staff = StaffService(self.session).create_staff(self._staff_payload())
        self.assertEqual(staff.personal_number, "PN-4001")

        service_record = ServiceRecordService(self.session).create_record(
            {
                "staff_id": staff.id,
                "designation": "Junior Clerk",
                "bps": 9,
                "employment_type": "Permanent",
                "employment_status": "Active",
                "date_first_appointment": date(2010, 1, 1),
                "selection_merit_number": 1,
            }
        )
        self.assertEqual(service_record.designation, "Junior Clerk")

        posting_service = PostingService(self.session)
        posting_service.add_first_posting(
            {
                "staff_id": staff.id,
                "station_name": "District Court Orakzai",
                "start_date": date(2010, 1, 1),
                "transfer_reason": "Initial posting",
            }
        )
        posting_service.execute_transfer(
            {
                "staff_id": staff.id,
                "new_station": "Record Branch",
                "transfer_date": date(2020, 1, 1),
                "transfer_reason": "Administrative need",
            }
        )
        self.assertEqual(
            self.session.execute(
                select(func.count(PostingTransfer.id)).where(
                    PostingTransfer.staff_id == staff.id
                )
            ).scalar_one(),
            2,
        )

        leave_result = LeaveService(self.session).process_leave(
            {
                "staff_id": staff.id,
                "leave_year": 2026,
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 1, 5),
                "reason": "Family work",
                "processed_by_admin_id": self.admin.id,
            }
        )
        self.assertEqual(leave_result["summary"]["remaining_days"], 20)

        seniority = SeniorityService(self.session).generate_seniority_list(
            "Junior Clerk"
        )
        self.assertEqual(seniority.ranked[0].personal_number, "PN-4001")

        report = ReportService(self.session).individual_profile("PN-4001")
        self.assertEqual(report.staff["personal_number"], "PN-4001")

        session_controller = SessionController()
        session_controller.start_session(self.admin.to_dict())
        session_controller.logout()
        self.assertFalse(session_controller.is_authenticated)

    def test_closing_and_reopening_session_preserves_data(self) -> None:
        staff = StaffService(self.session).create_staff(self._staff_payload())
        self.session.commit()
        self.session.close()

        reopened = self.session_factory()
        try:
            self.assertIsNotNone(reopened.get(StaffProfile, staff.id))
        finally:
            reopened.close()

    def test_navigation_opens_uc01_to_uc08_pages_without_duplicate_application(
        self,
    ) -> None:
        app = QApplication.instance() or QApplication([])
        original_app = QApplication.instance()
        window = MainWindow({"id": 1, "username": "admin", "full_name": "Admin"})

        labels = [
            window.button_group.button(index).text()
            for index in range(window.stack.count())
            if window.button_group.button(index) is not None
        ]

        self.assertIs(QApplication.instance(), original_app)
        self.assertIn("Dashboard", labels)
        self.assertIn("Staff Profiles", labels)
        self.assertIn("Service Records", labels)
        self.assertIn("Postings & Transfers", labels)
        self.assertIn("Leave Management", labels)
        self.assertIn("Seniority Lists", labels)
        self.assertIn("Reports & Printing", labels)
        self.assertGreaterEqual(window.stack.count(), 8)
        window.close()
        window.deleteLater()
        app.processEvents()


if __name__ == "__main__":
    unittest.main()
