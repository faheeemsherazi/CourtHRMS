from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from court_hrms.presentation.employee_quick_view_dialog import (
    EmployeeQuickViewDialog,
)


def _employee() -> dict:
    return {
        "personal_number": "240303426",
        "full_name": "Syed Muhammad Abdullah Shah Long Official Name",
        "father_name": "Syed Father Name",
        "cnic": "1730112345671",
        "date_of_birth": date(1980, 1, 1),
        "date_of_retirement": date(2040, 1, 1),
        "designation": "Junior Clerk",
        "bps": 11,
        "employment_type": "Permanent",
        "employment_status": "Active",
        "date_first_appointment": date(2010, 1, 1),
        "date_current_promotion": date(2020, 1, 1),
        "current_posting": "District Court Orakzai",
        "mobile_number": "03001234567",
        "domicile": "Orakzai",
        "district": "Orakzai",
    }


def test_quick_view_buttons_emit_navigation_requests(qtbot) -> None:
    dialog = EmployeeQuickViewDialog(_employee())
    qtbot.addWidget(dialog)

    with qtbot.waitSignal(dialog.open_full_profile_requested) as profile_signal:
        qtbot.mouseClick(dialog.profile_button, Qt.MouseButton.LeftButton)
    assert profile_signal.args == ["240303426"]

    dialog = EmployeeQuickViewDialog(_employee())
    qtbot.addWidget(dialog)
    with qtbot.waitSignal(dialog.open_service_history_requested) as service_signal:
        qtbot.mouseClick(dialog.service_button, Qt.MouseButton.LeftButton)
    assert service_signal.args == ["240303426"]

    dialog = EmployeeQuickViewDialog(_employee())
    qtbot.addWidget(dialog)
    with qtbot.waitSignal(dialog.open_posting_history_requested) as posting_signal:
        qtbot.mouseClick(dialog.posting_button, Qt.MouseButton.LeftButton)
    assert posting_signal.args == ["240303426"]


def test_quick_view_full_name_is_wrapped_and_selectable(qtbot) -> None:
    dialog = EmployeeQuickViewDialog(_employee())
    qtbot.addWidget(dialog)

    labels = dialog.findChildren(QLabel)
    matching_labels = [
        label for label in labels if label.text() == _employee()["full_name"]
    ]

    assert any(label.wordWrap() for label in matching_labels)
    assert any(
        label.textInteractionFlags() & Qt.TextInteractionFlag.TextSelectableByMouse
        for label in matching_labels
    )
