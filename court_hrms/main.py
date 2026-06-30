from __future__ import annotations

import sys
from pathlib import Path


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication

from court_hrms.controllers.auth_controller import AuthController
from court_hrms.database.init_db import initialize_database
from court_hrms.presentation.login_window import LoginWindow
from court_hrms.presentation.main_window import MainWindow
from court_hrms.presentation.styles import apply_app_style


def main() -> int:
    initialize_database()

    app = QApplication(sys.argv)
    app.setApplicationName("District Court Orakzai HR Management System")
    apply_app_style(app)

    windows: dict[str, object] = {}

    def show_login() -> None:
        login_window = LoginWindow(AuthController())
        windows["login"] = login_window
        login_window.login_successful.connect(show_main)
        login_window.show()

    def show_main(admin: dict) -> None:
        main_window = MainWindow(admin)
        windows["main"] = main_window
        main_window.logout_requested.connect(show_login)
        main_window.show()

        login_window = windows.get("login")
        if login_window is not None:
            login_window.close()

    show_login()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

