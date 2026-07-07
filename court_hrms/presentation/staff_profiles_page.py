from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate, QRegularExpression, Qt, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from court_hrms.controllers.employee_lookup_controller import EmployeeLookupController
from court_hrms.controllers.staff_controller import StaffController
from court_hrms.presentation.employee_quick_view_dialog import EmployeeQuickViewDialog
from court_hrms.presentation.table_utils import (
    EmployeeSummaryPanel,
    configure_professional_table,
    make_table_item,
)
from court_hrms.utils.date_utils import calculate_retirement_date, format_date
from court_hrms.utils.message_box import show_error, show_info


class StaffProfilesPage(QWidget):
    employee_navigation_requested = Signal(str, str)

    def __init__(self, controller: StaffController):
        super().__init__()
        self.controller = controller
        self.lookup_controller = EmployeeLookupController()
        self.current_staff_id: int | None = None
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(24, 24, 24, 24)
        page_layout.setSpacing(16)

        title = QLabel("Staff Profiles")
        title.setObjectName("PageTitle")
        page_layout.addWidget(title)

        search_card = QFrame()
        search_card.setObjectName("Card")
        search_layout = QHBoxLayout(search_card)
        search_layout.setContentsMargins(16, 14, 16, 14)
        search_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by personal number")
        self.search_input.returnPressed.connect(self._search_profile)

        search_button = QPushButton("Search")
        search_button.setObjectName("PrimaryButton")
        search_button.clicked.connect(self._search_profile)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_form)

        search_layout.addWidget(QLabel("Personal Number"))
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(search_button)
        search_layout.addWidget(clear_button)
        page_layout.addWidget(search_card)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        form_group = QGroupBox("Profile Information")
        form_layout = QGridLayout(form_group)
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(10)

        self.personal_number_input = QLineEdit()
        self.full_name_input = QLineEdit()
        self.father_name_input = QLineEdit()
        self.cnic_input = QLineEdit()
        self.cnic_input.setMaxLength(13)
        self.cnic_input.setValidator(
            QRegularExpressionValidator(
                QRegularExpression(r"\d{0,13}"), self.cnic_input
            )
        )
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        self.dob_input.setMinimumDate(QDate(1940, 1, 1))
        self.dob_input.setMaximumDate(QDate.currentDate().addYears(-18))
        self.dob_input.setDate(QDate.currentDate().addYears(-30))
        self.dob_input.dateChanged.connect(self._update_retirement_preview)

        self.gender_input = self._combo(["", "Male", "Female", "Other"])
        self.religion_input = self._combo(
            ["", "Islam", "Christianity", "Hinduism", "Other"]
        )
        self.marital_status_input = self._combo(
            ["", "Single", "Married", "Widowed", "Divorced"]
        )
        self.domicile_input = QLineEdit()
        self.district_input = QLineEdit()
        self.tehsil_input = QLineEdit()
        self.mobile_number_input = QLineEdit()
        self.mobile_number_input.setMaxLength(11)
        self.mobile_number_input.setValidator(
            QRegularExpressionValidator(
                QRegularExpression(r"\d{0,11}"), self.mobile_number_input
            )
        )
        self.email_input = QLineEdit()
        self.emergency_contact_input = QLineEdit()
        self.emergency_contact_input.setMaxLength(17)
        self.emergency_contact_input.setValidator(
            QRegularExpressionValidator(
                QRegularExpression(r"\d{0,17}"),
                self.emergency_contact_input,
            )
        )
        self.qualification_input = QLineEdit()
        self.retirement_preview = QLineEdit()
        self.retirement_preview.setReadOnly(True)

        self.present_address_input = QTextEdit()
        self.present_address_input.setFixedHeight(72)
        self.permanent_address_input = QTextEdit()
        self.permanent_address_input.setFixedHeight(72)

        fields = [
            ("Personal Number", self.personal_number_input),
            ("Full Name", self.full_name_input),
            ("Father Name", self.father_name_input),
            ("CNIC", self.cnic_input),
            ("Date of Birth", self.dob_input),
            ("Retirement Date", self.retirement_preview),
            ("Gender", self.gender_input),
            ("Religion", self.religion_input),
            ("Marital Status", self.marital_status_input),
            ("Domicile", self.domicile_input),
            ("District", self.district_input),
            ("Tehsil", self.tehsil_input),
            ("Mobile Number", self.mobile_number_input),
            ("Email", self.email_input),
            ("Emergency Contact", self.emergency_contact_input),
            ("Qualification", self.qualification_input),
        ]

        for index, (label, widget) in enumerate(fields):
            row = index // 2
            col = (index % 2) * 2
            form_layout.addWidget(QLabel(label), row, col)
            form_layout.addWidget(widget, row, col + 1)

        address_row = (len(fields) + 1) // 2
        form_layout.addWidget(QLabel("Present Address"), address_row, 0)
        form_layout.addWidget(self.present_address_input, address_row, 1)
        form_layout.addWidget(QLabel("Permanent Address"), address_row, 2)
        form_layout.addWidget(self.permanent_address_input, address_row, 3)

        button_row = address_row + 1
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Profile")
        self.add_button.setObjectName("GoldButton")
        self.add_button.clicked.connect(self._add_profile)

        self.update_button = QPushButton("Update Profile")
        self.update_button.setObjectName("PrimaryButton")
        self.update_button.setEnabled(False)
        self.update_button.clicked.connect(self._update_profile)

        form_clear_button = QPushButton("Clear Form")
        form_clear_button.clicked.connect(self.clear_form)

        button_layout.addStretch(1)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(form_clear_button)
        form_layout.addLayout(button_layout, button_row, 0, 1, 4)

        content_layout.addWidget(form_group)

        table_title = QLabel("Staff Register")
        table_title.setObjectName("SectionTitle")
        content_layout.addWidget(table_title)

        self.employee_summary = EmployeeSummaryPanel()
        content_layout.addWidget(self.employee_summary)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Personal #",
                "Full Name",
                "Father Name",
                "CNIC",
                "Mobile",
                "District",
                "Retirement",
            ]
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnHidden(0, True)
        self.table.setMinimumHeight(260)
        configure_professional_table(self.table, settings_key="staff_register")
        self.table.itemSelectionChanged.connect(self._load_selected_row)
        self.table.itemDoubleClicked.connect(self._open_quick_view_for_row)
        content_layout.addWidget(self.table, 1)

        scroll.setWidget(content)
        page_layout.addWidget(scroll, 1)

        self._update_retirement_preview()

    @staticmethod
    def _combo(items: list[str]) -> QComboBox:
        combo = QComboBox()
        combo.addItems(items)
        return combo

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

    def _update_retirement_preview(self) -> None:
        birth_date = self._qdate_to_date(self.dob_input.date())
        self.retirement_preview.setText(
            format_date(calculate_retirement_date(birth_date))
        )

    def _collect_form_data(self) -> dict:
        return {
            "personal_number": self.personal_number_input.text(),
            "full_name": self.full_name_input.text(),
            "father_name": self.father_name_input.text(),
            "cnic": self.cnic_input.text(),
            "date_of_birth": self._qdate_to_date(self.dob_input.date()),
            "gender": self.gender_input.currentText(),
            "religion": self.religion_input.currentText(),
            "marital_status": self.marital_status_input.currentText(),
            "domicile": self.domicile_input.text(),
            "district": self.district_input.text(),
            "tehsil": self.tehsil_input.text(),
            "mobile_number": self.mobile_number_input.text(),
            "email": self.email_input.text(),
            "present_address": self.present_address_input.toPlainText(),
            "permanent_address": self.permanent_address_input.toPlainText(),
            "emergency_contact": self.emergency_contact_input.text(),
            "qualification": self.qualification_input.text(),
        }

    def _add_profile(self) -> None:
        ok, message, profile = self.controller.create_profile(self._collect_form_data())
        if not ok:
            show_error(self, message)
            return
        self.current_staff_id = profile["id"]
        self.refresh()
        self._load_profile(profile)
        show_info(self, message)

    def _update_profile(self) -> None:
        if self.current_staff_id is None:
            show_error(self, "Select a staff profile before updating.")
            return

        ok, message, profile = self.controller.update_profile(
            self.current_staff_id,
            self._collect_form_data(),
        )
        if not ok:
            show_error(self, message)
            return
        self.refresh()
        self._load_profile(profile)
        show_info(self, message)

    def _search_profile(self) -> None:
        ok, message, profile = self.controller.search_by_personal_number(
            self.search_input.text()
        )
        if not ok:
            show_error(self, message, "Search")
            return
        self._load_profile(profile)

    def open_employee(self, personal_number: str) -> None:
        self.search_input.setText(personal_number)
        self._search_profile()

    def _load_selected_row(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if item is None:
            return
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self._load_profile(data)
            self._load_employee_summary(data.get("id"))

    def _load_profile(self, profile: dict) -> None:
        self.current_staff_id = profile.get("id")
        self.personal_number_input.setText(profile.get("personal_number") or "")
        self.full_name_input.setText(profile.get("full_name") or "")
        self.father_name_input.setText(profile.get("father_name") or "")
        self.cnic_input.setText(profile.get("cnic") or "")
        self._set_date(self.dob_input, profile.get("date_of_birth"))
        self._set_combo(self.gender_input, profile.get("gender"))
        self._set_combo(self.religion_input, profile.get("religion"))
        self._set_combo(self.marital_status_input, profile.get("marital_status"))
        self.domicile_input.setText(profile.get("domicile") or "")
        self.district_input.setText(profile.get("district") or "")
        self.tehsil_input.setText(profile.get("tehsil") or "")
        self.mobile_number_input.setText(profile.get("mobile_number") or "")
        self.email_input.setText(profile.get("email") or "")
        self.present_address_input.setPlainText(profile.get("present_address") or "")
        self.permanent_address_input.setPlainText(
            profile.get("permanent_address") or ""
        )
        self.emergency_contact_input.setText(profile.get("emergency_contact") or "")
        self.qualification_input.setText(profile.get("qualification") or "")
        self.retirement_preview.setText(format_date(profile.get("date_of_retirement")))
        self.update_button.setEnabled(True)
        self._load_employee_summary(self.current_staff_id)

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
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if item is None:
            return
        profile = item.data(Qt.ItemDataRole.UserRole)
        if not profile:
            return
        ok, message, employee = self.lookup_controller.by_staff_id(profile["id"])
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

    def clear_form(self) -> None:
        self.current_staff_id = None
        for line_edit in [
            self.search_input,
            self.personal_number_input,
            self.full_name_input,
            self.father_name_input,
            self.cnic_input,
            self.domicile_input,
            self.district_input,
            self.tehsil_input,
            self.mobile_number_input,
            self.email_input,
            self.emergency_contact_input,
            self.qualification_input,
        ]:
            line_edit.clear()

        self.present_address_input.clear()
        self.permanent_address_input.clear()
        self.dob_input.setDate(QDate.currentDate().addYears(-30))
        for combo in [
            self.gender_input,
            self.religion_input,
            self.marital_status_input,
        ]:
            combo.setCurrentIndex(0)
        self.table.clearSelection()
        self.employee_summary.clear()
        self.update_button.setEnabled(False)
        self._update_retirement_preview()

    def refresh(self) -> None:
        profiles = self.controller.list_profiles()
        self.table.setRowCount(len(profiles))
        for row, profile in enumerate(profiles):
            values = [
                profile.get("id"),
                profile.get("personal_number"),
                profile.get("full_name"),
                profile.get("father_name"),
                profile.get("cnic"),
                profile.get("mobile_number"),
                profile.get("district"),
                format_date(profile.get("date_of_retirement")),
            ]
            for column, value in enumerate(values):
                item = make_table_item(
                    value,
                    user_data=profile if column == 0 else None,
                )
                self.table.setItem(row, column, item)
