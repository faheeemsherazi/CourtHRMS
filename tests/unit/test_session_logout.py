from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from court_hrms.controllers.session_controller import SessionController
from court_hrms.main import ApplicationCoordinator
from court_hrms.utils.exceptions import AuthenticationRequiredError


class SessionLogoutTest(unittest.TestCase):
    def test_logout_clears_active_user(self) -> None:
        session = SessionController()
        session.start_session({"id": 1, "username": "admin"})

        session.logout()

        self.assertIsNone(session.active_user)

    def test_logout_clears_authentication_flag(self) -> None:
        session = SessionController()
        session.start_session({"id": 1, "username": "admin"})

        session.logout()

        self.assertFalse(session.is_authenticated)

    def test_logout_does_not_modify_database_records(self) -> None:
        session = SessionController()
        session.start_session({"id": 1, "username": "admin"})

        session.logout()

        self.assertIsNone(session.active_user)
        self.assertFalse(session.is_authenticated)

    def test_protected_action_fails_after_logout(self) -> None:
        session = SessionController()
        session.start_session({"id": 1, "username": "admin"})
        session.logout()

        with self.assertRaises(AuthenticationRequiredError):
            session.require_authenticated()

    def test_logout_with_missing_session_does_not_crash(self) -> None:
        session = SessionController()

        session.logout()

        self.assertFalse(session.is_authenticated)
        self.assertIsNone(session.active_user)

    def test_login_window_is_shown_after_logout_and_main_is_cleared(self) -> None:
        app = QApplication.instance() or QApplication([])
        coordinator = ApplicationCoordinator()
        original_app = QApplication.instance()

        coordinator.show_login()
        self.assertIsNotNone(coordinator.login_window)
        self.assertIsNone(coordinator.main_window)

        coordinator.show_main_window(
            {"id": 1, "username": "admin", "full_name": "Admin"}
        )
        self.assertIsNotNone(coordinator.main_window)
        self.assertIsNone(coordinator.login_window)

        coordinator.handle_logout()

        self.assertIs(QApplication.instance(), original_app)
        self.assertIsNotNone(coordinator.login_window)
        self.assertIsNone(coordinator.main_window)
        self.assertFalse(coordinator.session_controller.is_authenticated)
        coordinator.login_window.close()
        coordinator.login_window.deleteLater()
        app.processEvents()


if __name__ == "__main__":
    unittest.main()
