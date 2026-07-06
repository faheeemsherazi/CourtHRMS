from __future__ import annotations

from PySide6.QtWidgets import QMessageBox, QWidget


def show_error(
    parent: QWidget | None, message: str, title: str = "Validation Error"
) -> None:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Critical)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    box.exec()


def show_info(
    parent: QWidget | None, message: str, title: str = "District Court Orakzai HRMS"
) -> None:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Information)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    box.exec()


def confirm(
    parent: QWidget | None, message: str, title: str = "Confirm Action"
) -> bool:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    box.setDefaultButton(QMessageBox.StandardButton.No)
    return box.exec() == QMessageBox.StandardButton.Yes


def confirm_logout(parent: QWidget | None) -> bool:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle("Logout")
    box.setText("Logout from the system?\n\nAny unsaved form input will be discarded.")
    logout_button = box.addButton("Logout", QMessageBox.ButtonRole.AcceptRole)
    box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
    box.setDefaultButton(logout_button)
    box.exec()
    return box.clickedButton() == logout_button
