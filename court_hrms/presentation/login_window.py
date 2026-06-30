from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from court_hrms.controllers.auth_controller import AuthController
from court_hrms.utils.message_box import show_error


class LoginWindow(QWidget):
    login_successful = Signal(dict)

    def __init__(self, auth_controller: AuthController):
        super().__init__()
        self.auth_controller = auth_controller
        self.setWindowTitle("District Court Orakzai HR Management System - Login")
        self.setMinimumSize(980, 620)
        self.setObjectName("AppBackground")
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QGridLayout(self)
        outer.setContentsMargins(42, 42, 42, 42)
        outer.setHorizontalSpacing(24)

        brand = QFrame()
        brand.setObjectName("BrandPanel")
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(36, 36, 36, 36)
        brand_layout.setSpacing(16)

        seal = QLabel("DCO")
        seal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        seal.setFixedSize(86, 86)
        seal.setStyleSheet(
            "border: 2px solid #c9a227; border-radius: 43px; color: #c9a227; "
            "font-size: 20pt; font-weight: 800;"
        )

        title = QLabel("District Court\nOrakzai")
        title.setObjectName("BrandTitle")
        title.setWordWrap(True)

        subtitle = QLabel("Human Resource Management System")
        subtitle.setObjectName("BrandSubtitle")
        subtitle.setWordWrap(True)

        footer = QLabel("Authorized administrative access only")
        footer.setObjectName("BrandSubtitle")

        brand_layout.addWidget(seal)
        brand_layout.addSpacing(12)
        brand_layout.addWidget(title)
        brand_layout.addWidget(subtitle)
        brand_layout.addStretch(1)
        brand_layout.addWidget(footer)

        login_panel = QFrame()
        login_panel.setObjectName("LoginPanel")
        login_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        login_layout = QVBoxLayout(login_panel)
        login_layout.setContentsMargins(36, 34, 36, 34)
        login_layout.setSpacing(14)

        heading = QLabel("Secure Login")
        heading.setObjectName("PageTitle")
        subheading = QLabel("District Court Orakzai HR Management System")
        subheading.setObjectName("Muted")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setClearButtonEnabled(True)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self._attempt_login)

        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("PrimaryButton")
        self.login_button.clicked.connect(self._attempt_login)

        login_layout.addWidget(heading)
        login_layout.addWidget(subheading)
        login_layout.addSpacing(16)
        login_layout.addWidget(QLabel("Username"))
        login_layout.addWidget(self.username_input)
        login_layout.addWidget(QLabel("Password"))
        login_layout.addWidget(self.password_input)
        login_layout.addSpacing(8)
        login_layout.addWidget(self.login_button)

        outer.addWidget(brand, 0, 0)
        outer.addWidget(login_panel, 0, 1)
        outer.setColumnStretch(0, 5)
        outer.setColumnStretch(1, 4)

    def _attempt_login(self) -> None:
        ok, message, admin = self.auth_controller.login(
            self.username_input.text(),
            self.password_input.text(),
        )
        if not ok:
            show_error(self, message, "Login Failed")
            self.password_input.clear()
            self.password_input.setFocus()
            return

        self.login_successful.emit(admin)

    def reset(self) -> None:
        self.username_input.clear()
        self.password_input.clear()
        self.username_input.setFocus()

