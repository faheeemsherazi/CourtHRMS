from __future__ import annotations

import os
import tempfile
import unittest
from datetime import date
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from court_hrms.reporting.report_document_builder import ReportDocumentBuilder
from court_hrms.reporting.report_templates import build_seniority_list_html
from court_hrms.services.report_service import ReportService
from tests.integration.helpers import (
    add_admin,
    add_service_record,
    add_staff,
    create_test_session,
)


class ReportGenerationIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.engine, self.session = create_test_session()
        add_admin(self.session)
        staff = add_staff(self.session, "PN-3001")
        add_service_record(self.session, staff.id, "Junior Clerk", date(2010, 1, 1))

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_seniority_report_pdf_is_generated_from_service_result(self) -> None:
        report = ReportService(self.session).seniority_list("Junior Clerk")
        html = build_seniority_list_html(report)

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "seniority.pdf"
            ReportDocumentBuilder().export_pdf(html, output)

            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
