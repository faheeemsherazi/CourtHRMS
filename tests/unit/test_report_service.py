from __future__ import annotations

import os
import tempfile
import unittest
from datetime import date
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPageLayout
from PySide6.QtPrintSupport import QPrinter
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import sessionmaker

from court_hrms.database.db import Base
from court_hrms.models import (
    Admin,
    AnnualLeaveAccount,
    LeaveRecord,
    PostingTransfer,
    ServiceEvent,
    ServiceRecord,
    StaffProfile,
)
from court_hrms.reporting.report_document_builder import ReportDocumentBuilder
from court_hrms.reporting.report_templates import (
    build_professional_table,
    build_individual_profile_html,
    build_leave_history_html,
    build_posting_history_html,
    build_service_book_extract_html,
    build_transfer_history_html,
)
from court_hrms.services.leave_service import LeaveService
from court_hrms.services.posting_service import PostingService
from court_hrms.services.report_service import ReportService
from court_hrms.services.seniority_service import SeniorityService
from court_hrms.utils.exceptions import ReportDataNotFoundError
from court_hrms.utils.report_utils import sanitize_filename


class ReportServiceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

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
            username="admin", password_hash="hash", full_name="System Admin"
        )
        self.session.add(self.admin)
        self.session.flush()
        self.staff_one = self._add_staff(
            "PN-0001", "Ali & Sons <Test>", date(1980, 1, 1)
        )
        self.staff_two = self._add_staff("PN-0002", "Zahid Khan", date(1985, 1, 1))
        self._add_service(self.staff_one.id, "Junior Clerk", date(2010, 1, 1), merit=2)
        self._add_service(self.staff_two.id, "Junior Clerk", date(2012, 1, 1), merit=1)
        self.session.add(
            PostingTransfer(
                staff_id=self.staff_one.id,
                station_name="District Court Orakzai",
                start_date=date(2010, 1, 1),
                is_current=True,
                transfer_reason="Initial posting",
            )
        )
        self.session.flush()
        LeaveService(self.session).process_leave(
            {
                "staff_id": self.staff_one.id,
                "leave_year": 2026,
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 1, 5),
                "reason": "Family work",
                "processed_by_admin_id": self.admin.id,
            }
        )
        self.report_service = ReportService(self.session)

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def _add_staff(
        self, personal_number: str, full_name: str, birth: date
    ) -> StaffProfile:
        staff = StaffProfile(
            personal_number=personal_number,
            full_name=full_name,
            father_name="Father Name",
            cnic=f"173011230{personal_number[-4:]}",
            date_of_birth=birth,
            district="Orakzai",
            mobile_number="03001234567",
            present_address="District Court Orakzai",
            permanent_address="District Orakzai",
        )
        self.session.add(staff)
        self.session.flush()
        return staff

    def _add_service(
        self,
        staff_id: int,
        designation: str,
        appointment: date,
        merit: int,
    ) -> None:
        self.session.add(
            ServiceRecord(
                staff_id=staff_id,
                designation=designation,
                bps=9,
                employment_type="Permanent",
                employment_status="Active",
                date_first_appointment=appointment,
                selection_merit_number=merit,
            )
        )
        self.session.flush()

    def _table_counts(self) -> dict[str, int]:
        return {
            "staff": int(
                self.session.execute(select(func.count(StaffProfile.id))).scalar_one()
            ),
            "service": int(
                self.session.execute(select(func.count(ServiceRecord.id))).scalar_one()
            ),
            "posting": int(
                self.session.execute(
                    select(func.count(PostingTransfer.id))
                ).scalar_one()
            ),
            "accounts": int(
                self.session.execute(
                    select(func.count(AnnualLeaveAccount.id))
                ).scalar_one()
            ),
            "leave": int(
                self.session.execute(select(func.count(LeaveRecord.id))).scalar_one()
            ),
        }

    def test_individual_profile_report_returns_correct_staff(self) -> None:
        report = self.report_service.individual_profile("PN-0001")

        self.assertEqual(report.staff["personal_number"], "PN-0001")

    def test_individual_report_includes_service_data(self) -> None:
        report = self.report_service.individual_profile("PN-0001")

        self.assertEqual(report.service_record["designation"], "Junior Clerk")

    def test_individual_report_includes_posting_history(self) -> None:
        report = self.report_service.individual_profile("PN-0001")

        self.assertEqual(
            report.posting_history[0]["station_name"], "District Court Orakzai"
        )

    def test_individual_report_includes_leave_summary(self) -> None:
        report = self.report_service.individual_profile("PN-0001")

        self.assertEqual(report.leave_summaries[0]["availed_days"], 5)
        self.assertEqual(report.leave_summaries[0]["remaining_days"], 20)

    def test_leave_report_totals_match_leave_service(self) -> None:
        report = self.report_service.leave_history("PN-0001", 2026)
        summary = LeaveService(self.session).get_account_summary(
            self.staff_one.id, 2026
        )

        self.assertEqual(report.summaries[0]["availed_days"], summary["availed_days"])
        self.assertEqual(
            report.summaries[0]["remaining_days"], summary["remaining_days"]
        )

    def test_seniority_report_order_matches_seniority_service(self) -> None:
        report = self.report_service.seniority_list("Junior Clerk")
        service_result = SeniorityService(self.session).generate_seniority_list(
            "Junior Clerk"
        )

        self.assertEqual(
            [row["personal_number"] for row in report.ranked],
            [row.personal_number for row in service_result.ranked],
        )

    def test_no_data_report_raises_expected_error(self) -> None:
        with self.assertRaises(ReportDataNotFoundError):
            self.report_service.individual_profile("PN-9999")

    def test_pdf_export_creates_non_empty_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "report.pdf"
            ReportDocumentBuilder().export_pdf(
                "<html><body><h1>Report</h1></body></html>", output
            )

            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 0)

    def test_filenames_are_sanitized(self) -> None:
        self.assertEqual(
            sanitize_filename("Staff Profile PN/01:2026.pdf"),
            "Staff_Profile_PN_01_2026.pdf",
        )

    def test_report_generation_does_not_modify_database_data(self) -> None:
        before = self._table_counts()

        report = self.report_service.individual_profile("PN-0001")
        build_individual_profile_html(report)
        self.report_service.leave_history("PN-0001", 2026)
        self.report_service.seniority_list("Junior Clerk")

        self.assertEqual(before, self._table_counts())

    def test_missing_optional_values_render_safely(self) -> None:
        report = self.report_service.individual_profile("PN-0001")
        html = build_individual_profile_html(report)

        self.assertIn("—", html)

    def test_special_characters_do_not_break_html_report(self) -> None:
        report = self.report_service.individual_profile("PN-0001")
        html = build_individual_profile_html(report)

        self.assertIn("Ali &amp; Sons &lt;Test&gt;", html)

    def test_leave_history_html_contains_recorded_leave_reason(self) -> None:
        report = self.report_service.leave_history("PN-0001", 2026)
        html = build_leave_history_html(report)

        self.assertIn("Family work", html)

    def test_posting_history_report_returns_chronological_data(self) -> None:
        report = self.report_service.posting_history("PN-0001")
        html = build_posting_history_html(report)

        self.assertEqual(
            report.posting_history[0]["station_name"], "District Court Orakzai"
        )
        self.assertIn("Complete Posting History", html)

    def test_transfer_history_report_includes_order_reference(self) -> None:
        PostingService(self.session).execute_transfer(
            {
                "staff_id": self.staff_one.id,
                "new_station": "Record Branch",
                "transfer_date": date(2020, 1, 1),
                "order_number": "TR-1",
                "order_date": date(2019, 12, 31),
                "issuing_authority": "District & Sessions Judge, Orakzai",
            }
        )

        report = self.report_service.transfer_history("PN-0001")
        html = build_transfer_history_html(report)

        self.assertEqual(report.transfer_history[0]["order_number"], "TR-1")
        self.assertIn("TR-1", html)

    def test_service_book_report_includes_service_event(self) -> None:
        self.session.add(
            ServiceEvent(
                staff_id=self.staff_one.id,
                event_type="Promotion",
                effective_date=date(2021, 1, 1),
                order_number="PROM-1",
                new_designation="Senior Clerk",
                new_bps=14,
                station="District Court Orakzai",
                description="Promotion order.",
            )
        )
        self.session.flush()

        report = self.report_service.service_book_extract("PN-0001")
        html = build_service_book_extract_html(report)

        self.assertEqual(report.service_events[0]["event_type"], "Promotion")
        self.assertIn("PROM-1", html)

    def test_service_book_posting_transfer_layout_is_split_and_landscape(self) -> None:
        PostingService(self.session).execute_transfer(
            {
                "staff_id": self.staff_one.id,
                "new_station": "Sessions Court Administrative Branch Orakzai",
                "transfer_date": date(2020, 1, 1),
                "order_number": "DC-ORZ/HR/Posting-Transfer/2020/15",
                "order_date": date(2019, 12, 31),
                "issuing_authority": "District & Sessions Judge, Orakzai",
                "transfer_reason": "Administrative public interest posting order",
            }
        )

        report = self.report_service.service_book_extract("PN-0001")
        html = build_service_book_extract_html(report)

        self.assertIn('name="report-orientation" content="landscape"', html)
        self.assertIn("Posting / Transfer Order Details", html)
        self.assertIn("Relieving / Joining / Remarks Details", html)
        self.assertIn("Order<br>No.", html)
        self.assertIn("Movement</th>", html)
        self.assertNotIn("Movement Type</th>", html)
        self.assertNotIn("Order Number</th>", html)

    def test_narrow_report_layout_remains_portrait(self) -> None:
        report = self.report_service.individual_profile("PN-0001")
        html = build_individual_profile_html(report)

        self.assertIn('name="report-orientation" content="portrait"', html)

    def test_printer_uses_report_orientation_metadata(self) -> None:
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        ReportDocumentBuilder.configure_printer(
            printer,
            '<html><head><meta name="report-orientation" content="landscape"></head></html>',
        )

        self.assertEqual(
            printer.pageLayout().orientation(),
            QPageLayout.Orientation.Landscape,
        )

    def test_long_professional_tables_repeat_headers(self) -> None:
        columns = [
            "Serial",
            "From Station",
            "To Station",
            "Movement Type",
            "Order Number",
            "Order Date",
            "Effective Date",
            "Issuing Authority",
        ]
        rows = [
            [
                index,
                "District Court Orakzai",
                "Sessions Court Orakzai",
                "Transfer",
                f"DC-ORZ/HR/{index}/2026",
                date(2026, 7, 1),
                date(2026, 7, 2),
                "District & Sessions Judge, Orakzai",
            ]
            for index in range(1, 13)
        ]

        html = build_professional_table(
            rows,
            columns,
            profile="posting_transfer_order",
            landscape=True,
        )

        self.assertGreaterEqual(html.count("<thead><tr>"), 2)
        self.assertIn("page-break-before: always", html)

    def test_employee_dossier_includes_leave_ledger(self) -> None:
        report = self.report_service.employee_dossier("PN-0001")

        self.assertEqual(report.profile.staff["personal_number"], "PN-0001")
        self.assertTrue(report.leave_ledger)


if __name__ == "__main__":
    unittest.main()
