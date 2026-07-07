from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from court_hrms.controllers.employee_lookup_controller import EmployeeLookupController
from court_hrms.controllers.seniority_controller import SeniorityController
from court_hrms.presentation.employee_quick_view_dialog import EmployeeQuickViewDialog
from court_hrms.presentation.table_utils import (
    EmployeeSummaryPanel,
    configure_professional_table,
    make_table_item,
)
from court_hrms.utils.date_utils import format_date
from court_hrms.utils.datetime_utils import format_pakistan_datetime
from court_hrms.utils.message_box import show_error, show_info


class SeniorityPage(QWidget):
    employee_navigation_requested = Signal(str, str)

    def __init__(self, controller: SeniorityController):
        super().__init__()
        self.controller = controller
        self.lookup_controller = EmployeeLookupController()
        self.last_result: dict | None = None
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Seniority Lists")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        toolbar = QFrame()
        toolbar.setObjectName("Card")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 14, 16, 14)
        toolbar_layout.setSpacing(10)

        self.designation_input = QComboBox()
        self.designation_input.setMinimumWidth(260)

        self.status_label = QLabel("Employment Status: Active")
        self.status_label.setObjectName("Muted")

        generate_button = QPushButton("Generate List")
        generate_button.setObjectName("PrimaryButton")
        generate_button.clicked.connect(self._generate)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self._clear)

        toolbar_layout.addWidget(QLabel("Designation"))
        toolbar_layout.addWidget(self.designation_input)
        toolbar_layout.addWidget(self.status_label)
        toolbar_layout.addStretch(1)
        toolbar_layout.addWidget(generate_button)
        toolbar_layout.addWidget(refresh_button)
        toolbar_layout.addWidget(clear_button)
        layout.addWidget(toolbar)

        summary_row = QHBoxLayout()
        summary_row.setSpacing(12)
        self.summary_labels: dict[str, QLabel] = {}
        for label, key in [
            ("Selected Designation", "designation"),
            ("Ranked Employees", "ranked"),
            ("Excluded Employees", "excluded"),
            ("Generated", "generated"),
        ]:
            summary_row.addWidget(self._summary_card(label, key), 1)
        layout.addLayout(summary_row)

        self.empty_label = QLabel(
            "No eligible staff records were found for the selected designation."
        )
        self.empty_label.setObjectName("Muted")
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)

        self.employee_summary = EmployeeSummaryPanel()
        layout.addWidget(self.employee_summary)

        self.table = QTableWidget()
        self.table.setColumnCount(15)
        self.table.setHorizontalHeaderLabels(
            [
                "Rank",
                "Personal Number",
                "Full Name",
                "Father's Name",
                "Qualification",
                "Designation",
                "BPS",
                "Date of Birth",
                "First Entry in Government Service",
                "First Entry in Judiciary",
                "Current Post Date",
                "Promotion Date",
                "Retirement Date",
                "Current Posting",
                "Remarks",
            ]
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().setVisible(False)
        configure_professional_table(self.table, settings_key="seniority_list_register")
        self.table.setMinimumHeight(260)
        self.table.itemSelectionChanged.connect(self._load_selected_row_summary)
        self.table.itemDoubleClicked.connect(self._open_quick_view_for_row)
        layout.addWidget(self.table, 1)

        self.exclusions_group = QGroupBox("Excluded Records")
        exclusions_layout = QVBoxLayout(self.exclusions_group)
        self.exclusions_warning = QLabel(
            "Some employees were excluded because their Date of First Appointment is missing. "
            "Please update their service records."
        )
        self.exclusions_warning.setObjectName("Muted")
        exclusions_layout.addWidget(self.exclusions_warning)
        self.exclusions_table = QTableWidget()
        self.exclusions_table.setColumnCount(4)
        self.exclusions_table.setHorizontalHeaderLabels(
            ["Personal Number", "Full Name", "Designation", "Missing Field"]
        )
        self.exclusions_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.exclusions_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.exclusions_table.verticalHeader().setVisible(False)
        configure_professional_table(
            self.exclusions_table, settings_key="seniority_exclusions"
        )
        self.exclusions_table.setMinimumHeight(120)
        exclusions_layout.addWidget(self.exclusions_table)
        self.exclusions_group.setVisible(False)
        layout.addWidget(self.exclusions_group)

    def _summary_card(self, label: str, key: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        value = QLabel("—")
        value.setObjectName("MetricValue")
        caption = QLabel(label)
        caption.setObjectName("MetricLabel")
        value.setWordWrap(True)

        layout.addWidget(value)
        layout.addWidget(caption)
        self.summary_labels[key] = value
        return card

    @staticmethod
    def _format_datetime(value) -> str:
        if value is None:
            return ""
        if isinstance(value, datetime):
            return format_pakistan_datetime(value)
        return str(value)

    def _generate(self) -> None:
        designation = self.designation_input.currentText()
        ok, message, result = self.controller.generate_list(designation)
        if not ok or result is None:
            show_error(self, message, "Seniority Lists")
            return

        self.last_result = result
        self._render_result(result)
        if result.get("ranked_count", 0) == 0:
            self.empty_label.setVisible(True)
        show_info(self, message)

    def _render_result(self, result: dict) -> None:
        ranked = result.get("ranked") or []
        excluded = result.get("excluded") or []
        self.summary_labels["designation"].setText(result.get("designation") or "—")
        self.summary_labels["ranked"].setText(
            str(result.get("ranked_count", len(ranked)))
        )
        self.summary_labels["excluded"].setText(
            str(result.get("excluded_count", len(excluded)))
        )
        self.summary_labels["generated"].setText(
            self._format_datetime(result.get("generated_at"))
        )
        self._render_ranked_rows(ranked)
        self._render_exclusions(excluded)
        self.empty_label.setVisible(not ranked)

    def _render_ranked_rows(self, rows: list[dict]) -> None:
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = [
                row.get("rank"),
                row.get("personal_number"),
                row.get("full_name"),
                row.get("father_name"),
                row.get("qualification"),
                row.get("designation"),
                row.get("bps"),
                format_date(row.get("date_of_birth")),
                format_date(row.get("first_government_entry")),
                format_date(row.get("first_judiciary_entry")),
                format_date(row.get("current_post_date")),
                format_date(row.get("promotion_date")),
                format_date(row.get("retirement_date")),
                row.get("current_posting"),
                row.get("remarks"),
            ]
            for column, value in enumerate(values):
                item = make_table_item(
                    value,
                    user_data=row if column == 0 else None,
                    alignment=(
                        Qt.AlignmentFlag.AlignCenter
                        if column in (0, 6)
                        else Qt.AlignmentFlag.AlignLeft
                    ),
                )
                if column in (0, 6):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_index, column, item)

    def _render_exclusions(self, exclusions: list[dict]) -> None:
        self.exclusions_group.setVisible(bool(exclusions))
        self.exclusions_table.setRowCount(len(exclusions))
        for row_index, exclusion in enumerate(exclusions):
            values = [
                exclusion.get("personal_number"),
                exclusion.get("full_name"),
                exclusion.get("designation"),
                exclusion.get("missing_field"),
            ]
            for column, value in enumerate(values):
                self.exclusions_table.setItem(
                    row_index,
                    column,
                    make_table_item(value),
                )

    def _load_selected_row_summary(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            self.employee_summary.clear()
            return
        item = self.table.item(row, 0)
        if item is None:
            self.employee_summary.clear()
            return
        rank_row = item.data(Qt.ItemDataRole.UserRole)
        staff_id = rank_row.get("staff_id") if rank_row else None
        if staff_id is None:
            self.employee_summary.clear()
            return

        ok, _message, employee = self.lookup_controller.by_staff_id(staff_id)
        if ok:
            self.employee_summary.set_summary(employee)
        else:
            self.employee_summary.clear()

    def _open_quick_view_for_row(self, *_args) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if item is None:
            return
        rank_row = item.data(Qt.ItemDataRole.UserRole)
        staff_id = rank_row.get("staff_id") if rank_row else None
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

    def _clear(self) -> None:
        self.last_result = None
        for label in self.summary_labels.values():
            label.setText("—")
        self.table.setRowCount(0)
        self.exclusions_table.setRowCount(0)
        self.exclusions_group.setVisible(False)
        self.empty_label.setVisible(False)
        self.employee_summary.clear()

    def refresh(self) -> None:
        current = self.designation_input.currentText()
        self.designation_input.blockSignals(True)
        self.designation_input.clear()
        self.designation_input.addItems(self.controller.list_designations())
        if current:
            index = self.designation_input.findText(current)
            if index >= 0:
                self.designation_input.setCurrentIndex(index)
        self.designation_input.blockSignals(False)
