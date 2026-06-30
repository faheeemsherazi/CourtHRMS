from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from court_hrms.controllers.service_record_controller import ServiceRecordController
from court_hrms.utils.date_utils import format_date
from court_hrms.utils.message_box import show_error, show_info
from court_hrms.utils.validators import (
    DESIGNATION_BPS_RANGES,
    EMPLOYMENT_STATUSES,
    EMPLOYMENT_TYPES,
)


class ServiceRecordsPage(QWidget):
    def __init__(self, controller: ServiceRecordController):
        super().__init__()
        self.controller = controller
        self.selected_staff_id: int | None = None
        self.current_record_id: int | None = None
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Service Records")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        search_card = QFrame()
        search_card.setObjectName("Card")
        search_layout = QHBoxLayout(search_card)
        search_layout.setContentsMargins(16, 14, 16, 14)
        search_layout.setSpacing(10)

        self.staff_search_input = QLineEdit()
        self.staff_search_input.setPlaceholderText("Search staff by personal number")
        self.staff_search_input.returnPressed.connect(self._search_staff)

        search_button = QPushButton("Search Staff")
        search_button.setObjectName("PrimaryButton")
        search_button.clicked.connect(self._search_staff)

        self.staff_status = QLabel("No staff selected")
        self.staff_status.setObjectName("Muted")

        search_layout.addWidget(QLabel("Personal Number"))
        search_layout.addWidget(self.staff_search_input, 1)
        search_layout.addWidget(search_button)
        search_layout.addWidget(self.staff_status, 2)
        layout.addWidget(search_card)

        form_group = QGroupBox("Service Details")
        form_layout = QGridLayout(form_group)
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(10)

        self.designation_input = QComboBox()
        self.designation_input.addItems([""] + list(DESIGNATION_BPS_RANGES.keys()))

        self.bps_input = QSpinBox()
        self.bps_input.setRange(1, 22)

        self.employment_type_input = QComboBox()
        self.employment_type_input.addItems(list(EMPLOYMENT_TYPES))

        self.employment_status_input = QComboBox()
        self.employment_status_input.addItems(list(EMPLOYMENT_STATUSES))

        self.first_appointment_input = QDateEdit()
        self.first_appointment_input.setCalendarPopup(True)
        self.first_appointment_input.setDisplayFormat("yyyy-MM-dd")
        self.first_appointment_input.setMinimumDate(QDate(1940, 1, 1))
        self.first_appointment_input.setMaximumDate(QDate.currentDate().addYears(5))
        self.first_appointment_input.setDate(QDate.currentDate())

        self.has_promotion_checkbox = QCheckBox("Current promotion date")
        self.promotion_date_input = QDateEdit()
        self.promotion_date_input.setCalendarPopup(True)
        self.promotion_date_input.setDisplayFormat("yyyy-MM-dd")
        self.promotion_date_input.setMinimumDate(QDate(1940, 1, 1))
        self.promotion_date_input.setMaximumDate(QDate.currentDate().addYears(5))
        self.promotion_date_input.setDate(QDate.currentDate())
        self.promotion_date_input.setEnabled(False)
        self.has_promotion_checkbox.toggled.connect(self.promotion_date_input.setEnabled)

        self.merit_number_input = QLineEdit()
        self.merit_number_input.setPlaceholderText("Optional")
        self.remarks_input = QTextEdit()
        self.remarks_input.setFixedHeight(76)

        fields = [
            ("Designation", self.designation_input),
            ("BPS", self.bps_input),
            ("Employment Type", self.employment_type_input),
            ("Employment Status", self.employment_status_input),
            ("First Appointment", self.first_appointment_input),
            ("", self.has_promotion_checkbox),
            ("Merit Number", self.merit_number_input),
            ("Promotion Date", self.promotion_date_input),
        ]

        for index, (label, widget) in enumerate(fields):
            row = index // 2
            col = (index % 2) * 2
            if label:
                form_layout.addWidget(QLabel(label), row, col)
            form_layout.addWidget(widget, row, col + 1 if label else col, 1, 1 if label else 2)

        form_layout.addWidget(QLabel("Remarks"), 4, 0)
        form_layout.addWidget(self.remarks_input, 4, 1, 1, 3)

        buttons = QHBoxLayout()
        self.add_button = QPushButton("Add Service Record")
        self.add_button.setObjectName("GoldButton")
        self.add_button.clicked.connect(self._add_record)

        self.update_button = QPushButton("Update Service Record")
        self.update_button.setObjectName("PrimaryButton")
        self.update_button.setEnabled(False)
        self.update_button.clicked.connect(self._update_record)

        clear_button = QPushButton("Clear Form")
        clear_button.clicked.connect(self.clear_form)

        buttons.addStretch(1)
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.update_button)
        buttons.addWidget(clear_button)
        form_layout.addLayout(buttons, 5, 0, 1, 4)

        layout.addWidget(form_group)

        table_title = QLabel("Service Record Register")
        table_title.setObjectName("SectionTitle")
        layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Personal #",
                "Staff Name",
                "Designation",
                "BPS",
                "Type",
                "Status",
                "First Appointment",
                "Promotion",
            ]
        )
        self.table.setColumnHidden(0, True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._load_selected_row)
        layout.addWidget(self.table, 1)

    @staticmethod
    def _qdate_to_date(value: QDate) -> date:
        return date(value.year(), value.month(), value.day())

    @staticmethod
    def _set_date(edit: QDateEdit, value) -> None:
        if value:
            edit.setDate(QDate(value.year, value.month, value.day))

    @staticmethod
    def _set_combo(combo: QComboBox, value: str | None) -> None:
        index = combo.findText(value or "")
        combo.setCurrentIndex(index if index >= 0 else 0)

    def _collect_form_data(self) -> dict:
        return {
            "staff_id": self.selected_staff_id,
            "designation": self.designation_input.currentText(),
            "bps": self.bps_input.value(),
            "employment_type": self.employment_type_input.currentText(),
            "employment_status": self.employment_status_input.currentText(),
            "date_first_appointment": self._qdate_to_date(self.first_appointment_input.date()),
            "date_current_promotion": self._qdate_to_date(self.promotion_date_input.date())
            if self.has_promotion_checkbox.isChecked()
            else None,
            "selection_merit_number": self.merit_number_input.text(),
            "remarks": self.remarks_input.toPlainText(),
        }

    def _search_staff(self) -> None:
        ok, message, staff, record = self.controller.find_staff(self.staff_search_input.text())
        if not ok:
            show_error(self, message, "Staff Search")
            return

        self.selected_staff_id = staff["id"]
        self.staff_status.setText(f"{staff['personal_number']} - {staff['full_name']}")
        if record:
            self._load_record(record)
        else:
            self._clear_record_fields(keep_staff=True)

    def _add_record(self) -> None:
        if self.selected_staff_id is None:
            show_error(self, "Search and select a staff profile before adding a service record.")
            return

        ok, message, record = self.controller.create_record(self._collect_form_data())
        if not ok:
            show_error(self, message)
            return
        self.current_record_id = record["id"]
        self.refresh()
        self._load_record(record)
        show_info(self, message)

    def _update_record(self) -> None:
        if self.current_record_id is None:
            show_error(self, "Select a service record before updating.")
            return

        ok, message, record = self.controller.update_record(
            self.current_record_id,
            self._collect_form_data(),
        )
        if not ok:
            show_error(self, message)
            return
        self.refresh()
        self._load_record(record)
        show_info(self, message)

    def _load_selected_row(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if item is None:
            return
        record = item.data(Qt.ItemDataRole.UserRole)
        if record:
            self._load_record(record)

    def _load_record(self, record: dict) -> None:
        self.current_record_id = record.get("id")
        self.selected_staff_id = record.get("staff_id")
        self.staff_search_input.setText(record.get("staff_personal_number") or "")
        staff_name = record.get("staff_full_name") or "Selected staff"
        staff_number = record.get("staff_personal_number") or ""
        self.staff_status.setText(f"{staff_number} - {staff_name}".strip(" -"))
        self._set_combo(self.designation_input, record.get("designation"))
        self.bps_input.setValue(int(record.get("bps") or 1))
        self._set_combo(self.employment_type_input, record.get("employment_type"))
        self._set_combo(self.employment_status_input, record.get("employment_status"))
        self._set_date(self.first_appointment_input, record.get("date_first_appointment"))

        promotion_date = record.get("date_current_promotion")
        self.has_promotion_checkbox.setChecked(promotion_date is not None)
        if promotion_date:
            self._set_date(self.promotion_date_input, promotion_date)

        merit = record.get("selection_merit_number")
        self.merit_number_input.setText("" if merit is None else str(merit))
        self.remarks_input.setPlainText(record.get("remarks") or "")
        self.update_button.setEnabled(True)

    def _clear_record_fields(self, keep_staff: bool = False) -> None:
        self.current_record_id = None
        if not keep_staff:
            self.selected_staff_id = None
            self.staff_search_input.clear()
            self.staff_status.setText("No staff selected")
        self.designation_input.setCurrentIndex(0)
        self.bps_input.setValue(1)
        self.employment_type_input.setCurrentIndex(0)
        self.employment_status_input.setCurrentIndex(0)
        self.first_appointment_input.setDate(QDate.currentDate())
        self.has_promotion_checkbox.setChecked(False)
        self.promotion_date_input.setDate(QDate.currentDate())
        self.merit_number_input.clear()
        self.remarks_input.clear()
        self.update_button.setEnabled(False)

    def clear_form(self) -> None:
        self._clear_record_fields(keep_staff=False)
        self.table.clearSelection()

    def refresh(self) -> None:
        records = self.controller.list_records()
        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            values = [
                record.get("id"),
                record.get("staff_personal_number"),
                record.get("staff_full_name"),
                record.get("designation"),
                record.get("bps"),
                record.get("employment_type"),
                record.get("employment_status"),
                format_date(record.get("date_first_appointment")),
                format_date(record.get("date_current_promotion")),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem("" if value is None else str(value))
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, record)
                self.table.setItem(row, column, item)
