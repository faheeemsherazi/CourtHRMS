from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDateEdit,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from court_hrms.controllers.posting_controller import PostingController
from court_hrms.utils.date_utils import format_date
from court_hrms.utils.message_box import confirm, show_error, show_info


class PostingsTransfersPage(QWidget):
    def __init__(self, controller: PostingController):
        super().__init__()
        self.controller = controller
        self.selected_staff_id: int | None = None
        self.current_posting: dict | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(24, 24, 24, 24)
        page_layout.setSpacing(16)

        title = QLabel("Postings & Transfers")
        title.setObjectName("PageTitle")
        page_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

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

        current_group = QGroupBox("Current Posting")
        current_layout = QGridLayout(current_group)
        current_layout.setHorizontalSpacing(14)
        current_layout.setVerticalSpacing(10)

        self.current_station_display = QLineEdit()
        self.current_station_display.setReadOnly(True)
        self.current_start_display = QLineEdit()
        self.current_start_display.setReadOnly(True)
        self.current_end_display = QLineEdit()
        self.current_end_display.setReadOnly(True)

        current_layout.addWidget(QLabel("Current Station"), 0, 0)
        current_layout.addWidget(self.current_station_display, 0, 1)
        current_layout.addWidget(QLabel("Start Date"), 0, 2)
        current_layout.addWidget(self.current_start_display, 0, 3)
        current_layout.addWidget(QLabel("End Date"), 1, 0)
        current_layout.addWidget(self.current_end_display, 1, 1)
        layout.addWidget(current_group)

        forms_row = QHBoxLayout()
        forms_row.setSpacing(16)

        first_group = QGroupBox("First Posting")
        first_layout = QGridLayout(first_group)
        first_layout.setHorizontalSpacing(12)
        first_layout.setVerticalSpacing(10)

        self.first_station_input = QLineEdit()
        self.first_start_date_input = self._date_edit()
        self.first_reason_input = QTextEdit()
        self.first_reason_input.setFixedHeight(72)
        self.first_remarks_input = QTextEdit()
        self.first_remarks_input.setFixedHeight(72)

        first_layout.addWidget(QLabel("Station"), 0, 0)
        first_layout.addWidget(self.first_station_input, 0, 1)
        first_layout.addWidget(QLabel("Start Date"), 1, 0)
        first_layout.addWidget(self.first_start_date_input, 1, 1)
        first_layout.addWidget(QLabel("Reason"), 2, 0)
        first_layout.addWidget(self.first_reason_input, 2, 1)
        first_layout.addWidget(QLabel("Remarks"), 3, 0)
        first_layout.addWidget(self.first_remarks_input, 3, 1)

        add_first_button = QPushButton("Add First Posting")
        add_first_button.setObjectName("GoldButton")
        add_first_button.clicked.connect(self._add_first_posting)
        first_layout.addWidget(add_first_button, 4, 0, 1, 2)

        transfer_group = QGroupBox("Execute Transfer")
        transfer_layout = QGridLayout(transfer_group)
        transfer_layout.setHorizontalSpacing(12)
        transfer_layout.setVerticalSpacing(10)

        self.new_station_input = QLineEdit()
        self.transfer_date_input = self._date_edit()
        self.transfer_reason_input = QTextEdit()
        self.transfer_reason_input.setFixedHeight(72)
        self.transfer_remarks_input = QTextEdit()
        self.transfer_remarks_input.setFixedHeight(72)

        transfer_layout.addWidget(QLabel("New Station"), 0, 0)
        transfer_layout.addWidget(self.new_station_input, 0, 1)
        transfer_layout.addWidget(QLabel("Transfer Date"), 1, 0)
        transfer_layout.addWidget(self.transfer_date_input, 1, 1)
        transfer_layout.addWidget(QLabel("Reason"), 2, 0)
        transfer_layout.addWidget(self.transfer_reason_input, 2, 1)
        transfer_layout.addWidget(QLabel("Remarks"), 3, 0)
        transfer_layout.addWidget(self.transfer_remarks_input, 3, 1)

        transfer_button = QPushButton("Execute Transfer")
        transfer_button.setObjectName("PrimaryButton")
        transfer_button.clicked.connect(self._execute_transfer)
        transfer_layout.addWidget(transfer_button, 4, 0, 1, 2)

        forms_row.addWidget(first_group, 1)
        forms_row.addWidget(transfer_group, 1)
        layout.addLayout(forms_row)

        table_title = QLabel("Posting History")
        table_title.setObjectName("SectionTitle")
        layout.addWidget(table_title)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels(
            ["ID", "Station", "Start Date", "End Date", "Current", "Reason", "Remarks"]
        )
        self.history_table.setColumnHidden(0, True)
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setMinimumHeight(220)
        layout.addWidget(self.history_table, 1)

        scroll.setWidget(content)
        page_layout.addWidget(scroll, 1)

    @staticmethod
    def _date_edit() -> QDateEdit:
        edit = QDateEdit()
        edit.setCalendarPopup(True)
        edit.setDisplayFormat("yyyy-MM-dd")
        edit.setMinimumDate(QDate(1940, 1, 1))
        edit.setMaximumDate(QDate.currentDate().addYears(20))
        edit.setDate(QDate.currentDate())
        return edit

    @staticmethod
    def _qdate_to_date(value: QDate) -> date:
        return date(value.year(), value.month(), value.day())

    def _search_staff(self) -> None:
        self._load_staff_context(show_not_found=True)

    def _load_staff_context(self, show_not_found: bool = False) -> bool:
        ok, message, staff, current, history = self.controller.find_staff(self.staff_search_input.text())
        if not ok:
            self._clear_staff_context()
            if show_not_found:
                show_error(self, message, "Staff Search")
            return False

        self.selected_staff_id = staff["id"]
        service_status = "service record available" if staff.get("has_service_record") else "service record missing"
        self.staff_status.setText(f"{staff['personal_number']} - {staff['full_name']} ({service_status})")
        self.current_posting = current
        self._render_current_posting(current)
        self._render_history(history)
        return True

    def _clear_staff_context(self) -> None:
        self.selected_staff_id = None
        self.current_posting = None
        self.staff_status.setText("No staff selected")
        self._render_current_posting(None)
        self._render_history([])

    def _render_current_posting(self, posting: dict | None) -> None:
        if posting is None:
            self.current_station_display.setText("No current posting")
            self.current_start_display.clear()
            self.current_end_display.clear()
            return

        self.current_station_display.setText(posting.get("station_name") or "")
        self.current_start_display.setText(format_date(posting.get("start_date")))
        self.current_end_display.setText(format_date(posting.get("end_date")))

    def _render_history(self, history: list[dict]) -> None:
        self.history_table.setRowCount(len(history))
        for row, posting in enumerate(history):
            values = [
                posting.get("id"),
                posting.get("station_name"),
                format_date(posting.get("start_date")),
                format_date(posting.get("end_date")),
                "Yes" if posting.get("is_current") else "No",
                posting.get("transfer_reason"),
                posting.get("remarks"),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem("" if value is None else str(value))
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, posting)
                self.history_table.setItem(row, column, item)

    def _add_first_posting(self) -> None:
        if self.selected_staff_id is None:
            show_error(self, "Search and select a staff profile before adding a posting.")
            return

        data = {
            "staff_id": self.selected_staff_id,
            "station_name": self.first_station_input.text(),
            "start_date": self._qdate_to_date(self.first_start_date_input.date()),
            "transfer_reason": self.first_reason_input.toPlainText(),
            "remarks": self.first_remarks_input.toPlainText(),
        }
        ok, message, _posting = self.controller.add_first_posting(data)
        if not ok:
            show_error(self, message)
            return

        show_info(self, message)
        self.first_station_input.clear()
        self.first_reason_input.clear()
        self.first_remarks_input.clear()
        self._load_staff_context()

    def _execute_transfer(self) -> None:
        if self.selected_staff_id is None:
            show_error(self, "Search and select a staff profile before executing transfer.")
            return

        if self.current_posting is None:
            show_error(self, "No current posting was found. Add the first posting before transfer.")
            return

        if not confirm(self, "Execute transfer and update posting history?", "Confirm Transfer"):
            return

        data = {
            "staff_id": self.selected_staff_id,
            "new_station": self.new_station_input.text(),
            "transfer_date": self._qdate_to_date(self.transfer_date_input.date()),
            "transfer_reason": self.transfer_reason_input.toPlainText(),
            "remarks": self.transfer_remarks_input.toPlainText(),
        }
        ok, message, _posting = self.controller.execute_transfer(data)
        if not ok:
            show_error(self, message)
            return

        show_info(self, message)
        self.new_station_input.clear()
        self.transfer_reason_input.clear()
        self.transfer_remarks_input.clear()
        self._load_staff_context()

    def refresh(self) -> None:
        if self.selected_staff_id is not None:
            self._load_staff_context()
