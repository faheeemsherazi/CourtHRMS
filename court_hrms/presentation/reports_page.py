from __future__ import annotations

from datetime import date
from pathlib import Path

from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtPrintSupport import QPrintDialog, QPrinter, QPrinterInfo

from court_hrms.controllers.report_controller import (
    REPORT_EMPLOYEE_DOSSIER,
    REPORT_INDIVIDUAL_PROFILE,
    REPORT_LEAVE_HISTORY,
    REPORT_POSTING_HISTORY,
    REPORT_SENIORITY_LIST,
    REPORT_SERVICE_BOOK,
    REPORT_TRANSFER_HISTORY,
    ReportController,
)
from court_hrms.presentation.report_preview_dialog import ReportPreviewDialog
from court_hrms.reporting.report_document_builder import ReportDocumentBuilder
from court_hrms.utils.app_logger import get_logger
from court_hrms.utils.message_box import confirm, show_error, show_info


class ReportsPage(QWidget):
    def __init__(self, controller: ReportController):
        super().__init__()
        self.controller = controller
        self.logger = get_logger()
        self.last_report: dict | None = None
        self._build_ui()
        self.refresh()
        self._update_action_state()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Reports & Printing")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        selector = QFrame()
        selector.setObjectName("Card")
        selector_layout = QHBoxLayout(selector)
        selector_layout.setContentsMargins(16, 14, 16, 14)
        selector_layout.setSpacing(18)

        self.report_group = QButtonGroup(self)
        self.profile_radio = QRadioButton("Individual Staff Profile")
        self.leave_radio = QRadioButton("Leave History")
        self.seniority_radio = QRadioButton("Seniority List")
        self.posting_radio = QRadioButton("Posting History")
        self.transfer_radio = QRadioButton("Transfer History")
        self.service_book_radio = QRadioButton("Service Book")
        self.dossier_radio = QRadioButton("Employee Dossier")
        self.profile_radio.setChecked(True)

        for index, radio in enumerate(
            [
                self.profile_radio,
                self.leave_radio,
                self.seniority_radio,
                self.posting_radio,
                self.transfer_radio,
                self.service_book_radio,
                self.dossier_radio,
            ]
        ):
            self.report_group.addButton(radio, index)
            selector_layout.addWidget(radio)
        selector_layout.addStretch(1)
        self.report_group.idClicked.connect(self._handle_report_type_changed)
        layout.addWidget(selector)

        self.filter_stack = QStackedWidget()
        self.filter_stack.addWidget(self._build_profile_filters())
        self.filter_stack.addWidget(self._build_leave_filters())
        self.filter_stack.addWidget(self._build_seniority_filters())
        layout.addWidget(self.filter_stack)

        actions = QFrame()
        actions.setObjectName("Card")
        action_layout = QHBoxLayout(actions)
        action_layout.setContentsMargins(16, 14, 16, 14)
        action_layout.setSpacing(10)

        self.preview_button = QPushButton("Preview Report")
        self.preview_button.setObjectName("PrimaryButton")
        self.preview_button.clicked.connect(self._preview_report)

        self.export_button = QPushButton("Export PDF")
        self.export_button.setObjectName("GoldButton")
        self.export_button.clicked.connect(self._export_pdf)

        self.print_button = QPushButton("Print")
        self.print_button.clicked.connect(self._print_report)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self._clear)

        action_layout.addStretch(1)
        action_layout.addWidget(self.preview_button)
        action_layout.addWidget(self.export_button)
        action_layout.addWidget(self.print_button)
        action_layout.addWidget(clear_button)
        layout.addWidget(actions)
        layout.addStretch(1)

    def _build_profile_filters(self) -> QWidget:
        group = QGroupBox("Individual Staff Profile Filters")
        layout = QGridLayout(group)
        layout.setHorizontalSpacing(14)
        layout.setVerticalSpacing(10)
        self.profile_personal_input = QLineEdit()
        self.profile_personal_input.setPlaceholderText("Personal number")
        self.profile_personal_input.textChanged.connect(self._update_action_state)
        layout.addWidget(QLabel("Personal Number"), 0, 0)
        layout.addWidget(self.profile_personal_input, 0, 1)
        layout.setColumnStretch(1, 1)
        return group

    def _build_leave_filters(self) -> QWidget:
        group = QGroupBox("Leave History Filters")
        layout = QGridLayout(group)
        layout.setHorizontalSpacing(14)
        layout.setVerticalSpacing(10)
        self.leave_personal_input = QLineEdit()
        self.leave_personal_input.setPlaceholderText("Personal number")
        self.leave_personal_input.textChanged.connect(self._update_action_state)

        self.leave_year_input = QComboBox()
        self.leave_year_input.addItem("All Years")
        current_year = date.today().year
        for year in range(current_year + 1, current_year - 11, -1):
            self.leave_year_input.addItem(str(year))

        layout.addWidget(QLabel("Personal Number"), 0, 0)
        layout.addWidget(self.leave_personal_input, 0, 1)
        layout.addWidget(QLabel("Leave Year"), 0, 2)
        layout.addWidget(self.leave_year_input, 0, 3)
        layout.setColumnStretch(1, 1)
        return group

    def _build_seniority_filters(self) -> QWidget:
        group = QGroupBox("Seniority List Filters")
        layout = QGridLayout(group)
        layout.setHorizontalSpacing(14)
        layout.setVerticalSpacing(10)
        self.seniority_designation_input = QComboBox()
        self.seniority_designation_input.currentIndexChanged.connect(
            self._update_action_state
        )
        layout.addWidget(QLabel("Designation"), 0, 0)
        layout.addWidget(self.seniority_designation_input, 0, 1)
        layout.setColumnStretch(1, 1)
        return group

    def _handle_report_type_changed(self, index: int) -> None:
        self.filter_stack.setCurrentIndex(index if index in (0, 1, 2) else 0)
        self.last_report = None
        self._update_action_state()

    def _current_report_type(self) -> str:
        index = self.report_group.checkedId()
        if index == 0:
            return REPORT_INDIVIDUAL_PROFILE
        if index == 1:
            return REPORT_LEAVE_HISTORY
        if index == 2:
            return REPORT_SENIORITY_LIST
        if index == 3:
            return REPORT_POSTING_HISTORY
        if index == 4:
            return REPORT_TRANSFER_HISTORY
        if index == 5:
            return REPORT_SERVICE_BOOK
        return REPORT_EMPLOYEE_DOSSIER

    def _current_filters(self) -> dict:
        report_type = self._current_report_type()
        if report_type == REPORT_INDIVIDUAL_PROFILE:
            return {"personal_number": self.profile_personal_input.text()}
        if report_type == REPORT_LEAVE_HISTORY:
            return {
                "personal_number": self.leave_personal_input.text(),
                "leave_year": self.leave_year_input.currentText(),
            }
        if report_type in {
            REPORT_POSTING_HISTORY,
            REPORT_TRANSFER_HISTORY,
            REPORT_SERVICE_BOOK,
            REPORT_EMPLOYEE_DOSSIER,
        }:
            return {"personal_number": self.profile_personal_input.text()}
        return {"designation": self.seniority_designation_input.currentText()}

    def _filters_valid(self) -> bool:
        report_type = self._current_report_type()
        if report_type in {
            REPORT_INDIVIDUAL_PROFILE,
            REPORT_POSTING_HISTORY,
            REPORT_TRANSFER_HISTORY,
            REPORT_SERVICE_BOOK,
            REPORT_EMPLOYEE_DOSSIER,
        }:
            return bool(self.profile_personal_input.text().strip())
        if report_type == REPORT_LEAVE_HISTORY:
            return bool(self.leave_personal_input.text().strip())
        return bool(self.seniority_designation_input.currentText().strip())

    def _update_action_state(self) -> None:
        enabled = self._filters_valid()
        self.preview_button.setEnabled(enabled)
        self.export_button.setEnabled(enabled)
        self.print_button.setEnabled(enabled)

    def _prepare_report(self) -> dict | None:
        ok, message, report = self.controller.prepare_report(
            self._current_report_type(),
            self._current_filters(),
        )
        if not ok or report is None:
            show_error(self, message, "Reports & Printing")
            return None
        self.last_report = report
        return report

    def _preview_report(self) -> None:
        report = self._prepare_report()
        if report is None:
            return
        ReportPreviewDialog.show(self, report["html"], report["title"])

    def _export_pdf(self) -> None:
        report = self._prepare_report()
        if report is None:
            return

        default_path = str(Path.home() / report["default_filename"])
        path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export PDF Report",
            default_path,
            "PDF Files (*.pdf)",
        )
        if not path:
            return

        output_path = Path(path)
        if output_path.exists() and not confirm(
            self,
            "A file with this name already exists. Overwrite it?",
            "Confirm Overwrite",
        ):
            return

        ok, message, _path = self.controller.export_pdf(report["html"], output_path)
        if ok:
            show_info(self, message)
        else:
            show_error(self, message, "PDF Export")

    def _print_report(self) -> None:
        report = self._prepare_report()
        if report is None:
            return

        if not QPrinterInfo.availablePrinters():
            show_error(self, "No printer is available on this system.", "Print")
            return

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        ReportDocumentBuilder.configure_printer(printer, report["html"])
        dialog = QPrintDialog(printer, self)
        dialog.setWindowTitle("Print HR Report")
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        document = ReportDocumentBuilder.build_document(report["html"])
        try:
            document.print_(printer)
            self.logger.info("Print dispatched; report_type=%s", report["report_type"])
        except Exception:
            self.logger.exception("Print dispatch failed")
            show_error(self, "The report could not be printed.", "Print")

    def _clear(self) -> None:
        self.last_report = None
        self.profile_personal_input.clear()
        self.leave_personal_input.clear()
        self.leave_year_input.setCurrentIndex(0)
        if self.seniority_designation_input.count() > 0:
            self.seniority_designation_input.setCurrentIndex(0)
        self.profile_radio.setChecked(True)
        self.filter_stack.setCurrentIndex(0)
        self._update_action_state()

    def refresh(self) -> None:
        current = self.seniority_designation_input.currentText()
        self.seniority_designation_input.blockSignals(True)
        self.seniority_designation_input.clear()
        self.seniority_designation_input.addItems(self.controller.list_designations())
        if current:
            index = self.seniority_designation_input.findText(current)
            if index >= 0:
                self.seniority_designation_input.setCurrentIndex(index)
        self.seniority_designation_input.blockSignals(False)
        self._update_action_state()
