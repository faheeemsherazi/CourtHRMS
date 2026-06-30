from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from court_hrms.controllers.posting_controller import PostingController
from court_hrms.controllers.service_record_controller import ServiceRecordController
from court_hrms.controllers.staff_controller import StaffController
from court_hrms.controllers.admin_account_controller import AdminAccountController
from court_hrms.presentation.admin_account_page import AdminAccountPage
from court_hrms.presentation.dashboard_page import DashboardPage
from court_hrms.presentation.postings_transfers_page import PostingsTransfersPage
from court_hrms.presentation.service_records_page import ServiceRecordsPage
from court_hrms.presentation.staff_profiles_page import StaffProfilesPage
from court_hrms.utils.message_box import confirm


class MainWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(self, admin: dict):
        super().__init__()
        self.admin = admin
        self.setWindowTitle("District Court Orakzai HR Management System")
        self.resize(1360, 820)

        self.staff_controller = StaffController()
        self.service_record_controller = ServiceRecordController()
        self.posting_controller = PostingController()
        self.admin_account_controller = AdminAccountController()

        self._build_ui()
        self._show_page(0)

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("AppBackground")
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 22, 18, 18)
        sidebar_layout.setSpacing(8)

        side_title = QLabel("District Court\nOrakzai HRMS")
        side_title.setObjectName("SidebarTitle")
        side_title.setWordWrap(True)
        self.side_subtitle = QLabel()
        self.side_subtitle.setObjectName("SidebarSubtitle")
        self.side_subtitle.setWordWrap(True)
        self._update_signed_in_label()

        sidebar_layout.addWidget(side_title)
        sidebar_layout.addWidget(self.side_subtitle)
        sidebar_layout.addSpacing(18)

        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage(
            self.staff_controller,
            self.service_record_controller,
            self.posting_controller,
        )
        self.staff_page = StaffProfilesPage(self.staff_controller)
        self.service_records_page = ServiceRecordsPage(self.service_record_controller)
        self.postings_page = PostingsTransfersPage(self.posting_controller)
        self.admin_account_page = AdminAccountPage(self.admin_account_controller, self.admin)
        self.admin_account_page.account_updated.connect(self._handle_account_updated)

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.staff_page)
        self.stack.addWidget(self.service_records_page)
        self.stack.addWidget(self.postings_page)
        self.stack.addWidget(self.admin_account_page)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        nav_items = [
            ("Dashboard", 0),
            ("Staff Profiles", 1),
            ("Service Records", 2),
            ("Postings & Transfers", 3),
            ("Admin Account", 4),
        ]
        for label, index in nav_items:
            button = QPushButton(label)
            button.setObjectName("SidebarButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, i=index: self._show_page(i))
            self.button_group.addButton(button, index)
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch(1)

        logout_button = QPushButton("Logout")
        logout_button.setObjectName("SidebarButton")
        logout_button.clicked.connect(self._logout)
        sidebar_layout.addWidget(logout_button)

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.stack, 1)
        self.setCentralWidget(root)

    def _show_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        button = self.button_group.button(index)
        if button:
            button.setChecked(True)

        current_page = self.stack.currentWidget()
        refresh = getattr(current_page, "refresh", None)
        if callable(refresh):
            refresh()

    def _handle_account_updated(self, admin: dict) -> None:
        self.admin = admin
        self._update_signed_in_label()

    def _update_signed_in_label(self) -> None:
        self.side_subtitle.setText(
            f"Signed in: {self.admin.get('full_name') or self.admin.get('username')}"
        )

    def _logout(self) -> None:
        if confirm(self, "Do you want to log out of the HR Management System?", "Logout"):
            self.logout_requested.emit()
            self.close()
