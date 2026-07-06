from __future__ import annotations

import sys
from pathlib import Path


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication

from court_hrms.controllers.auth_controller import AuthController
from court_hrms.controllers.session_controller import SessionController
from court_hrms.database.init_db import initialize_database
from court_hrms.presentation.login_window import LoginWindow
from court_hrms.presentation.main_window import MainWindow
from court_hrms.presentation.styles import apply_app_style
from court_hrms.utils.app_logger import get_logger


class ApplicationCoordinator:
    def __init__(self):
        self.session_controller = SessionController()
        self.login_window: LoginWindow | None = None
        self.main_window: MainWindow | None = None

    def show_login(self) -> None:
        if self.main_window is not None:
            self.main_window.close()
            self.main_window.deleteLater()
            self.main_window = None

        self.login_window = LoginWindow(AuthController())
        self.login_window.login_successful.connect(self.show_main_window)
        self.login_window.reset()
        self.login_window.show()

    def show_main_window(self, admin: dict) -> None:
        self.session_controller.start_session(admin)
        self.main_window = MainWindow(admin, self.session_controller)
        self.main_window.logout_requested.connect(self.handle_logout)
        self.main_window.show()

        if self.login_window is not None:
            self.login_window.close()
            self.login_window.deleteLater()
            self.login_window = None

    def handle_logout(self) -> None:
        if self.session_controller.is_authenticated:
            self.session_controller.logout()
        self.show_login()


def main() -> int:
    logger = get_logger()
    logger.info("Application startup")
    initialize_database()

    app = QApplication(sys.argv)
    app.setApplicationName("District Court Orakzai HR Management System")
    apply_app_style(app)

    coordinator = ApplicationCoordinator()
    coordinator.show_login()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
