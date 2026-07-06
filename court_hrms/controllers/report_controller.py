from __future__ import annotations

from datetime import datetime
from pathlib import Path

from court_hrms.database.db import session_scope
from court_hrms.reporting.report_document_builder import ReportDocumentBuilder
from court_hrms.reporting.report_templates import (
    build_individual_profile_html,
    build_leave_history_html,
    build_seniority_list_html,
)
from court_hrms.services.report_service import ReportService
from court_hrms.services.seniority_service import SeniorityService
from court_hrms.utils.app_logger import get_logger
from court_hrms.utils.exceptions import ReportGenerationError
from court_hrms.utils.report_utils import sanitize_filename
from court_hrms.utils.validators import ValidationError


REPORT_INDIVIDUAL_PROFILE = "individual_profile"
REPORT_LEAVE_HISTORY = "leave_history"
REPORT_SENIORITY_LIST = "seniority_list"


class ReportController:
    def __init__(self):
        self.builder = ReportDocumentBuilder()
        self.logger = get_logger()

    def prepare_report(
        self, report_type: str, filters: dict
    ) -> tuple[bool, str, dict | None]:
        try:
            with session_scope() as session:
                service = ReportService(session)
                if report_type == REPORT_INDIVIDUAL_PROFILE:
                    dto = service.individual_profile(filters.get("personal_number", ""))
                    html = build_individual_profile_html(dto)
                    filename = self._profile_filename(dto.staff.get("personal_number"))
                    title = "Individual Staff Profile"
                elif report_type == REPORT_LEAVE_HISTORY:
                    year = filters.get("leave_year")
                    dto = service.leave_history(
                        filters.get("personal_number", ""),
                        None if year in (None, "", "All Years") else int(year),
                    )
                    html = build_leave_history_html(dto)
                    filename = self._leave_filename(
                        dto.staff.get("personal_number"), dto.selected_year
                    )
                    title = "Leave History"
                elif report_type == REPORT_SENIORITY_LIST:
                    dto = service.seniority_list(filters.get("designation", ""))
                    html = build_seniority_list_html(dto)
                    filename = self._seniority_filename(dto.designation)
                    title = "Seniority List"
                else:
                    return False, "Report type is not valid.", None

            self.logger.info("Report prepared; type=%s title=%s", report_type, title)
            return (
                True,
                "Report prepared.",
                {
                    "html": html,
                    "default_filename": filename,
                    "title": title,
                    "report_type": report_type,
                },
            )
        except ValidationError as exc:
            return False, str(exc), None
        except Exception:
            self.logger.exception("Unexpected report preparation failure")
            return False, "The report could not be prepared.", None

    def list_designations(self) -> list[str]:
        with session_scope() as session:
            return SeniorityService(session).list_designations()

    def export_pdf(
        self, html: str, output_path: str | Path
    ) -> tuple[bool, str, Path | None]:
        try:
            path = self.builder.export_pdf(html, output_path)
            self.logger.info("PDF report exported; path=%s", path)
            return True, "PDF report exported successfully.", path
        except ReportGenerationError:
            self.logger.exception("PDF report export failed")
            return (
                False,
                "The PDF report could not be generated.\n"
                "Please verify the selected location and try again.",
                None,
            )

    @staticmethod
    def _date_suffix() -> str:
        return datetime.now().strftime("%Y%m%d")

    def _profile_filename(self, personal_number: str | None) -> str:
        return sanitize_filename(
            f"Staff_Profile_{personal_number or 'Unknown'}_{self._date_suffix()}.pdf"
        )

    def _leave_filename(
        self, personal_number: str | None, leave_year: int | None
    ) -> str:
        year = "All_Years" if leave_year is None else str(leave_year)
        return sanitize_filename(
            f"Leave_History_{personal_number or 'Unknown'}_{year}_{self._date_suffix()}.pdf"
        )

    def _seniority_filename(self, designation: str) -> str:
        return sanitize_filename(f"Seniority_{designation}_{self._date_suffix()}.pdf")
