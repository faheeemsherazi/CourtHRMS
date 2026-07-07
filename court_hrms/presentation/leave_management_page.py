from __future__ import annotations

from datetime import date, datetime

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDateEdit,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from court_hrms.controllers.employee_lookup_controller import EmployeeLookupController
from court_hrms.controllers.leave_controller import LeaveController
from court_hrms.presentation.employee_quick_view_dialog import EmployeeQuickViewDialog
from court_hrms.presentation.table_utils import (
    EmployeeSummaryPanel,
    configure_professional_table,
    make_table_item,
)
from court_hrms.utils.date_utils import format_date
from court_hrms.utils.datetime_utils import format_pakistan_datetime
from court_hrms.utils.message_box import show_error, show_info


class LeaveManagementPage(QWidget):
    employee_navigation_requested = Signal(str, str)

    def __init__(self, controller: LeaveController):
        super().__init__()
        self.controller = controller
        self.lookup_controller = EmployeeLookupController()
        self.selected_staff_id: int | None = None
        self.selected_staff: dict | None = None
        self._build_ui()
        self._clear_staff_context()
        self._update_date_bounds()
        self._recalculate_days()

    def _build_ui(self) -> None:
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(24, 24, 24, 24)
        page_layout.setSpacing(16)

        title = QLabel("Leave Management")
        title.setObjectName("PageTitle")
        page_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(self._build_search_card())
        self.employee_summary = EmployeeSummaryPanel()
        layout.addWidget(self.employee_summary)
        layout.addLayout(self._build_summary_cards())
        layout.addWidget(self._build_leave_form())
        layout.addWidget(self._build_history_section(), 1)

        scroll.setWidget(content)
        page_layout.addWidget(scroll, 1)

    def _build_search_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QGridLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search staff by personal number")
        self.search_input.returnPressed.connect(self._search_staff)

        search_button = QPushButton("Search")
        search_button.setObjectName("PrimaryButton")
        search_button.clicked.connect(self._search_staff)

        clear_button = QPushButton("Clear Selection")
        clear_button.clicked.connect(self._clear_staff_context)

        self.staff_name_display = QLineEdit()
        self.staff_name_display.setReadOnly(True)
        self.designation_display = QLineEdit()
        self.designation_display.setReadOnly(True)
        self.bps_display = QLineEdit()
        self.bps_display.setReadOnly(True)
        self.status_display = QLineEdit()
        self.status_display.setReadOnly(True)

        layout.addWidget(QLabel("Personal Number"), 0, 0)
        layout.addWidget(self.search_input, 0, 1)
        layout.addWidget(search_button, 0, 2)
        layout.addWidget(clear_button, 0, 3)
        layout.addWidget(QLabel("Staff Name"), 1, 0)
        layout.addWidget(self.staff_name_display, 1, 1)
        layout.addWidget(QLabel("Designation"), 1, 2)
        layout.addWidget(self.designation_display, 1, 3)
        layout.addWidget(QLabel("BPS"), 2, 0)
        layout.addWidget(self.bps_display, 2, 1)
        layout.addWidget(QLabel("Employment Status"), 2, 2)
        layout.addWidget(self.status_display, 2, 3)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        return card

    def _build_summary_cards(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)
        self.summary_labels: dict[str, QLabel] = {}
        for label, key in [
            ("Selected Year", "year"),
            ("Entitlement", "entitlement"),
            ("Availed", "availed"),
            ("Remaining", "remaining"),
        ]:
            row.addWidget(self._summary_card(label, key), 1)
        return row

    def _summary_card(self, label: str, key: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        value = QLabel("0")
        value.setObjectName("MetricValue")
        caption = QLabel(label)
        caption.setObjectName("MetricLabel")

        layout.addWidget(value)
        layout.addWidget(caption)
        self.summary_labels[key] = value
        return card

    def _build_leave_form(self) -> QGroupBox:
        group = QGroupBox("Leave Details")
        layout = QGridLayout(group)
        layout.setHorizontalSpacing(14)
        layout.setVerticalSpacing(10)

        current_year = date.today().year
        self.year_input = QSpinBox()
        self.year_input.setRange(1900, 9999)
        self.year_input.setValue(current_year)
        self.year_input.valueChanged.connect(self._handle_year_changed)

        self.start_date_input = self._date_edit(current_year)
        self.end_date_input = self._date_edit(current_year)
        self.start_date_input.dateChanged.connect(self._recalculate_days)
        self.end_date_input.dateChanged.connect(self._recalculate_days)

        self.days_display = QLineEdit()
        self.days_display.setReadOnly(True)

        self.reason_input = QTextEdit()
        self.reason_input.setFixedHeight(70)
        self.remarks_input = QTextEdit()
        self.remarks_input.setFixedHeight(70)

        self.process_button = QPushButton("Process Leave")
        self.process_button.setObjectName("PrimaryButton")
        self.process_button.clicked.connect(self._process_leave)

        clear_button = QPushButton("Clear Form")
        clear_button.clicked.connect(self._clear_leave_form)

        layout.addWidget(QLabel("Leave Year"), 0, 0)
        layout.addWidget(self.year_input, 0, 1)
        layout.addWidget(QLabel("Start Date"), 0, 2)
        layout.addWidget(self.start_date_input, 0, 3)
        layout.addWidget(QLabel("End Date"), 1, 0)
        layout.addWidget(self.end_date_input, 1, 1)
        layout.addWidget(QLabel("Calculated Days"), 1, 2)
        layout.addWidget(self.days_display, 1, 3)
        layout.addWidget(QLabel("Reason"), 2, 0)
        layout.addWidget(self.reason_input, 2, 1, 1, 3)
        layout.addWidget(QLabel("Remarks"), 3, 0)
        layout.addWidget(self.remarks_input, 3, 1, 1, 3)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.process_button)
        buttons.addWidget(clear_button)
        layout.addLayout(buttons, 4, 0, 1, 4)
        return group

    def _build_history_section(self) -> QGroupBox:
        group = QGroupBox("Year-wise Leave History")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 18, 12, 12)
        layout.setSpacing(8)

        self.empty_history_label = QLabel(
            "No leave records were found for the selected year."
        )
        self.empty_history_label.setObjectName("Muted")
        layout.addWidget(self.empty_history_label)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(9)
        self.history_table.setHorizontalHeaderLabels(
            [
                "Record ID",
                "Year",
                "Start Date",
                "End Date",
                "Days",
                "Reason",
                "Remarks",
                "Recorded At",
                "Processed By",
            ]
        )
        self.history_table.setColumnHidden(0, True)
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.history_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.history_table.verticalHeader().setVisible(False)
        configure_professional_table(self.history_table, settings_key="leave_history")
        self.history_table.itemSelectionChanged.connect(self._load_selected_row_summary)
        self.history_table.itemDoubleClicked.connect(self._open_quick_view_for_row)
        self.history_table.setMinimumHeight(240)
        layout.addWidget(self.history_table, 1)
        return group

    @staticmethod
    def _date_edit(year: int) -> QDateEdit:
        edit = QDateEdit()
        edit.setCalendarPopup(True)
        edit.setDisplayFormat("yyyy-MM-dd")
        edit.setMinimumDate(QDate(year, 1, 1))
        edit.setMaximumDate(QDate(year, 12, 31))
        edit.setDate(QDate(year, 1, 1))
        return edit

    @staticmethod
    def _qdate_to_date(value: QDate) -> date:
        return date(value.year(), value.month(), value.day())

    @staticmethod
    def _format_datetime(value) -> str:
        if value is None:
            return ""
        if isinstance(value, datetime):
            return format_pakistan_datetime(value)
        return format_date(value)

    def _handle_year_changed(self) -> None:
        self._update_date_bounds()
        self._recalculate_days()
        if self.selected_staff_id is not None:
            self._refresh_selected_year()

    def _update_date_bounds(self) -> None:
        year = self.year_input.value()
        minimum = QDate(year, 1, 1)
        maximum = QDate(year, 12, 31)
        for edit in [self.start_date_input, self.end_date_input]:
            edit.blockSignals(True)
            edit.setMinimumDate(minimum)
            edit.setMaximumDate(maximum)
            if edit.date().year() != year:
                edit.setDate(minimum)
            edit.blockSignals(False)

    def _recalculate_days(self) -> None:
        ok, message, days = self.controller.calculate_days(
            self._qdate_to_date(self.start_date_input.date()),
            self._qdate_to_date(self.end_date_input.date()),
        )
        self.days_display.setText(str(days) if ok and days is not None else "")
        self.days_display.setToolTip("" if ok else message)

    def _search_staff(self) -> None:
        ok, message, context = self.controller.find_staff(
            self.search_input.text(),
            self.year_input.value(),
        )
        if not ok or context is None:
            self._clear_staff_context()
            show_error(self, message, "Staff Search")
            return

        self.selected_staff = context["staff"]
        self.selected_staff_id = self.selected_staff["id"]
        self._render_staff(self.selected_staff, context.get("service_record"))
        self._render_summary(context["summary"])
        self._render_history(context["history"])
        self._load_employee_summary(self.selected_staff_id)
        self.process_button.setEnabled(True)

    def _render_staff(self, staff: dict, service_record: dict | None) -> None:
        self.staff_name_display.setText(staff.get("full_name") or "")
        self.designation_display.setText(
            service_record.get("designation") if service_record else ""
        )
        bps = service_record.get("bps") if service_record else ""
        self.bps_display.setText("" if bps is None else str(bps))
        self.status_display.setText(
            service_record.get("employment_status") if service_record else ""
        )

    def _render_summary(self, summary: dict) -> None:
        self.summary_labels["year"].setText(
            str(summary.get("leave_year") or self.year_input.value())
        )
        self.summary_labels["entitlement"].setText(
            str(summary.get("entitlement_days") or 0)
        )
        self.summary_labels["availed"].setText(str(summary.get("availed_days") or 0))
        self.summary_labels["remaining"].setText(
            str(summary.get("remaining_days") or 0)
        )

    def _render_history(self, history: list[dict]) -> None:
        self.empty_history_label.setVisible(not history)
        self.history_table.setRowCount(len(history))
        for row, record in enumerate(history):
            values = [
                record.get("id"),
                record.get("leave_year"),
                format_date(record.get("start_date")),
                format_date(record.get("end_date")),
                record.get("days_availed"),
                record.get("reason"),
                record.get("remarks"),
                self._format_datetime(record.get("created_at")),
                record.get("processed_by"),
            ]
            for column, value in enumerate(values):
                item = make_table_item(
                    value,
                    user_data=record if column == 0 else None,
                    alignment=(
                        Qt.AlignmentFlag.AlignCenter
                        if column in (1, 4)
                        else Qt.AlignmentFlag.AlignLeft
                    ),
                )
                self.history_table.setItem(row, column, item)

    def _load_selected_row_summary(self) -> None:
        row = self.history_table.currentRow()
        if row < 0:
            if self.selected_staff_id is None:
                self.employee_summary.clear()
            return
        item = self.history_table.item(row, 0)
        record = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        staff_id = (record or {}).get("staff_id") or self.selected_staff_id
        self._load_employee_summary(staff_id)

    def _load_employee_summary(self, staff_id: int | None) -> None:
        if staff_id is None:
            self.employee_summary.clear()
            return

        ok, _message, employee = self.lookup_controller.by_staff_id(staff_id)
        if ok:
            self.employee_summary.set_summary(employee)
        else:
            self.employee_summary.clear()

    def _open_quick_view_for_row(self, *_args) -> None:
        row = self.history_table.currentRow()
        if row < 0:
            return
        item = self.history_table.item(row, 0)
        record = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        staff_id = (record or {}).get("staff_id") or self.selected_staff_id
        if staff_id is None:
            return

        ok, message, employee = self.lookup_controller.by_staff_id(staff_id)
        if not ok or employee is None:
            show_error(self, message, "Employee Quick View")
            return
        self._show_employee_quick_view(employee)

    def _show_employee_quick_view(self, employee: dict) -> None:
        dialog = EmployeeQuickViewDialog(employee, self)
        dialog.open_full_profile_requested.connect(
            lambda personal_number: self.employee_navigation_requested.emit(
                "profile", personal_number
            )
        )
        dialog.open_service_history_requested.connect(
            lambda personal_number: self.employee_navigation_requested.emit(
                "service", personal_number
            )
        )
        dialog.open_posting_history_requested.connect(
            lambda personal_number: self.employee_navigation_requested.emit(
                "posting", personal_number
            )
        )
        dialog.exec()

    def _refresh_selected_year(self) -> None:
        if self.selected_staff_id is None:
            return

        ok, message, summary = self.controller.get_summary(
            self.selected_staff_id,
            self.year_input.value(),
        )
        if not ok or summary is None:
            show_error(self, message)
            return
        ok, message, history = self.controller.list_history(
            self.selected_staff_id,
            self.year_input.value(),
        )
        if not ok:
            show_error(self, message)
            return
        self._render_summary(summary)
        self._render_history(history)

    def _collect_form_data(self) -> dict:
        return {
            "staff_id": self.selected_staff_id,
            "leave_year": self.year_input.value(),
            "start_date": self._qdate_to_date(self.start_date_input.date()),
            "end_date": self._qdate_to_date(self.end_date_input.date()),
            "days_availed": self.days_display.text(),
            "reason": self.reason_input.toPlainText(),
            "remarks": self.remarks_input.toPlainText(),
        }

    def _process_leave(self) -> None:
        if self.selected_staff_id is None:
            show_error(
                self, "Search and select a staff profile before processing leave."
            )
            return

        self.process_button.setEnabled(False)
        try:
            ok, message, result = self.controller.process_leave(
                self._collect_form_data()
            )
            if not ok or result is None:
                show_error(self, message)
                return
            self._render_summary(result["summary"])
            self._refresh_selected_year()
            self.reason_input.clear()
            self.remarks_input.clear()
            show_info(self, message)
        finally:
            self.process_button.setEnabled(self.selected_staff_id is not None)

    def _clear_leave_form(self) -> None:
        self._update_date_bounds()
        self.start_date_input.setDate(QDate(self.year_input.value(), 1, 1))
        self.end_date_input.setDate(QDate(self.year_input.value(), 1, 1))
        self.reason_input.clear()
        self.remarks_input.clear()
        self._recalculate_days()

    def _clear_staff_context(self) -> None:
        self.selected_staff_id = None
        self.selected_staff = None
        self.search_input.clear()
        self.staff_name_display.clear()
        self.designation_display.clear()
        self.bps_display.clear()
        self.status_display.clear()
        self.employee_summary.clear()
        self._render_summary(
            {
                "leave_year": (
                    self.year_input.value()
                    if hasattr(self, "year_input")
                    else date.today().year
                ),
                "entitlement_days": 25,
                "availed_days": 0,
                "remaining_days": 25,
            }
        )
        if hasattr(self, "history_table"):
            self._render_history([])
        if hasattr(self, "process_button"):
            self.process_button.setEnabled(False)

    def refresh(self) -> None:
        if self.selected_staff_id is not None:
            self._refresh_selected_year()
