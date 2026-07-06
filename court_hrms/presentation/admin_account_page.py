from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from court_hrms.controllers.admin_account_controller import AdminAccountController
from court_hrms.utils.message_box import show_error, show_info


class AdminAccountPage(QWidget):
    account_updated = Signal(dict)

    def __init__(self, controller: AdminAccountController, admin: dict):
        super().__init__()
        self.controller = controller
        self.admin = admin
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Admin Account")
        title.setObjectName("PageTitle")
        subtitle = QLabel(
            "Change the administrator username, display name, or password."
        )
        subtitle.setObjectName("Muted")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        self.account_summary = QLabel("")
        self.account_summary.setObjectName("SectionTitle")
        card_layout.addWidget(self.account_summary)

        form_group = QGroupBox("Account Details")
        form = QGridLayout(form_group)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        self.username_input = QLineEdit()
        self.full_name_input = QLineEdit()
        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.current_password_input.setPlaceholderText("Required to save changes")
        self.new_password_input.setPlaceholderText(
            "Leave blank to keep current password"
        )
        self.confirm_password_input.setPlaceholderText("Repeat new password")

        form.addWidget(QLabel("Username"), 0, 0)
        form.addWidget(self.username_input, 0, 1)
        form.addWidget(QLabel("Full Name"), 1, 0)
        form.addWidget(self.full_name_input, 1, 1)
        form.addWidget(QLabel("Current Password"), 2, 0)
        form.addWidget(self.current_password_input, 2, 1)
        form.addWidget(QLabel("New Password"), 3, 0)
        form.addWidget(self.new_password_input, 3, 1)
        form.addWidget(QLabel("Confirm Password"), 4, 0)
        form.addWidget(self.confirm_password_input, 4, 1)

        buttons = QHBoxLayout()
        save_button = QPushButton("Save Account")
        save_button.setObjectName("PrimaryButton")
        save_button.clicked.connect(self._save_account)

        clear_password_button = QPushButton("Clear Password Fields")
        clear_password_button.clicked.connect(self._clear_password_fields)

        buttons.addStretch(1)
        buttons.addWidget(save_button)
        buttons.addWidget(clear_password_button)
        form.addLayout(buttons, 5, 0, 1, 2)

        card_layout.addWidget(form_group)
        layout.addWidget(card)
        layout.addStretch(1)

    def refresh(self) -> None:
        admin_id = self.admin.get("id")
        if admin_id:
            latest = self.controller.get_admin(admin_id)
            if latest:
                self.admin = latest

        self.username_input.setText(self.admin.get("username") or "")
        self.full_name_input.setText(self.admin.get("full_name") or "")
        self.account_summary.setText(
            f"Signed in as {self.admin.get('full_name') or self.admin.get('username')}"
        )
        self._clear_password_fields()

    def _collect_data(self) -> dict:
        return {
            "username": self.username_input.text(),
            "full_name": self.full_name_input.text(),
            "current_password": self.current_password_input.text(),
            "new_password": self.new_password_input.text(),
            "confirm_password": self.confirm_password_input.text(),
        }

    def _save_account(self) -> None:
        ok, message, admin = self.controller.update_account(
            self.admin["id"],
            self._collect_data(),
        )
        if not ok:
            show_error(self, message)
            return

        self.admin = admin
        self.account_updated.emit(admin)
        self.refresh()
        show_info(self, message)

    def _clear_password_fields(self) -> None:
        self.current_password_input.clear()
        self.new_password_input.clear()
        self.confirm_password_input.clear()
