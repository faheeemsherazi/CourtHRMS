from __future__ import annotations

from PySide6.QtCore import Signal
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

from court_hrms.controllers.leave_controller import LeaveController
from court_hrms.controllers.posting_controller import PostingController
from court_hrms.controllers.report_controller import ReportController
from court_hrms.controllers.service_record_controller import ServiceRecordController
from court_hrms.controllers.session_controller import SessionController
from court_hrms.controllers.seniority_controller import SeniorityController
from court_hrms.controllers.staff_controller import StaffController
from court_hrms.controllers.admin_account_controller import AdminAccountController
from court_hrms.presentation.admin_account_page import AdminAccountPage
from court_hrms.presentation.dashboard_page import DashboardPage
from court_hrms.presentation.leave_management_page import LeaveManagementPage
from court_hrms.presentation.postings_transfers_page import PostingsTransfersPage
from court_hrms.presentation.reports_page import ReportsPage
from court_hrms.presentation.service_records_page import ServiceRecordsPage
from court_hrms.presentation.seniority_page import SeniorityPage
from court_hrms.presentation.staff_profiles_page import StaffProfilesPage
from court_hrms.utils.message_box import confirm_logout


class MainWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(
        self, admin: dict, session_controller: SessionController | None = None
    ):
        super().__init__()
        self.admin = admin
        self.session_controller = session_controller
        self.setWindowTitle("District Court Orakzai HR Management System")
        self.resize(1360, 820)

        self.staff_controller = StaffController()
        self.service_record_controller = ServiceRecordController()
        self.posting_controller = PostingController()
        self.leave_controller = LeaveController(self.admin)
        self.seniority_controller = SeniorityController()
        self.report_controller = ReportController()
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
        self.leave_page = LeaveManagementPage(self.leave_controller)
        self.seniority_page = SeniorityPage(self.seniority_controller)
        self.reports_page = ReportsPage(self.report_controller)
        self.admin_account_page = AdminAccountPage(
            self.admin_account_controller, self.admin
        )
        self.admin_account_page.account_updated.connect(self._handle_account_updated)

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.staff_page)
        self.stack.addWidget(self.service_records_page)
        self.stack.addWidget(self.postings_page)
        self.stack.addWidget(self.leave_page)
        self.stack.addWidget(self.seniority_page)
        self.stack.addWidget(self.reports_page)
        self.stack.addWidget(self.admin_account_page)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        nav_items = [
            ("Dashboard", 0),
            ("Staff Profiles", 1),
            ("Service Records", 2),
            ("Postings & Transfers", 3),
            ("Leave Management", 4),
            ("Seniority Lists", 5),
            ("Reports & Printing", 6),
            ("Admin Account", 7),
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
        self.leave_controller.set_authenticated_admin(admin)
        self._update_signed_in_label()

    def _update_signed_in_label(self) -> None:
        self.side_subtitle.setText(
            f"Signed in: {self.admin.get('full_name') or self.admin.get('username')}"
        )

    def _logout(self) -> None:
        if confirm_logout(self):
            self.clear_session_state()
            self.logout_requested.emit()
            self.close()

    def clear_session_state(self) -> None:
        self.admin = {}
        self.leave_controller.clear_session()
        if self.session_controller is not None:
            self.session_controller.logout()

        for page in [
            self.staff_page,
            self.service_records_page,
            self.postings_page,
            self.leave_page,
            self.seniority_page,
            self.reports_page,
        ]:
            clear = getattr(page, "clear_form", None)
            if callable(clear):
                clear()
        self.postings_page._clear_staff_context()
        self.leave_page._clear_staff_context()
        self.seniority_page._clear()
        self.reports_page._clear()
