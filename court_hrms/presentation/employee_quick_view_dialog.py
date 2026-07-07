from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from court_hrms.utils.date_utils import format_date


class EmployeeQuickViewDialog(QDialog):
    open_full_profile_requested = Signal(str)
    open_service_history_requested = Signal(str)
    open_posting_history_requested = Signal(str)

    def __init__(self, employee: dict, parent=None):
        super().__init__(parent)
        self.employee = employee
        self.personal_number = employee.get("personal_number") or ""
        self.setWindowTitle("Employee Quick View")
        self.setMinimumWidth(680)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        title = QLabel(self.employee.get("full_name") or "Employee")
        title.setObjectName("SectionTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(8)
        rows = [
            ("Full Name", self.employee.get("full_name")),
            ("Personal Number", self.employee.get("personal_number")),
            ("Father's Name", self.employee.get("father_name")),
            ("CNIC", self.employee.get("cnic")),
            ("Date of Birth", format_date(self.employee.get("date_of_birth"))),
            (
                "Retirement Date",
                format_date(self.employee.get("date_of_retirement")),
            ),
            ("Designation", self.employee.get("designation")),
            ("BPS", self.employee.get("bps")),
            ("Employment Type", self.employee.get("employment_type")),
            ("Employment Status", self.employee.get("employment_status")),
            (
                "First Appointment",
                format_date(self.employee.get("date_first_appointment")),
            ),
            (
                "Current Promotion",
                format_date(self.employee.get("date_current_promotion")),
            ),
            ("Current Posting", self.employee.get("current_posting")),
            ("Mobile Number", self.employee.get("mobile_number")),
            ("Domicile", self.employee.get("domicile")),
            ("District", self.employee.get("district")),
        ]
        for index, (label_text, value) in enumerate(rows):
            row = index // 2
            col = (index % 2) * 2
            label = QLabel(label_text)
            label.setObjectName("Muted")
            value_label = QLabel("" if value is None else str(value))
            value_label.setWordWrap(True)
            value_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            value_label.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Preferred,
            )
            grid.addWidget(label, row, col)
            grid.addWidget(value_label, row, col + 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        layout.addLayout(grid)

        buttons = QDialogButtonBox()
        self.profile_button = QPushButton("Open Full Profile")
        self.service_button = QPushButton("Open Service History")
        self.posting_button = QPushButton("Open Posting History")
        close_button = buttons.addButton(QDialogButtonBox.StandardButton.Close)
        buttons.addButton(self.profile_button, QDialogButtonBox.ButtonRole.ActionRole)
        buttons.addButton(self.service_button, QDialogButtonBox.ButtonRole.ActionRole)
        buttons.addButton(self.posting_button, QDialogButtonBox.ButtonRole.ActionRole)
        close_button.clicked.connect(self.reject)
        self.profile_button.clicked.connect(self._open_full_profile)
        self.service_button.clicked.connect(self._open_service_history)
        self.posting_button.clicked.connect(self._open_posting_history)
        layout.addWidget(buttons)

    def _open_full_profile(self) -> None:
        self.open_full_profile_requested.emit(self.personal_number)
        self.accept()

    def _open_service_history(self) -> None:
        self.open_service_history_requested.emit(self.personal_number)
        self.accept()

    def _open_posting_history(self) -> None:
        self.open_posting_history_requested.emit(self.personal_number)
        self.accept()
