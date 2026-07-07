from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QTableWidget

from court_hrms.presentation.table_utils import (
    EmployeeSummaryPanel,
    configure_professional_table,
    make_table_item,
)


def test_table_item_stores_full_value_in_tooltip_role(qtbot) -> None:
    table = QTableWidget(1, 2)
    qtbot.addWidget(table)
    table.setHorizontalHeaderLabels(["Personal Number", "Full Name"])
    configure_professional_table(table, settings_key="test_tooltips")

    full_name = "Syed Muhammad Abdullah Shah Long Official Name"
    table.setItem(0, 0, make_table_item("240303426"))
    table.setItem(0, 1, make_table_item(full_name))

    assert table.item(0, 1).data(Qt.ItemDataRole.ToolTipRole) == full_name
    assert table.horizontalHeaderItem(1).text() == "Full Name"
    assert (
        table.horizontalHeaderItem(1).data(Qt.ItemDataRole.ToolTipRole) == "Full Name"
    )


def test_professional_table_keeps_headers_and_horizontal_scroll(qtbot) -> None:
    headers = [
        "Rank",
        "Personal Number",
        "Full Name",
        "Father's Name",
        "Qualification",
        "Designation",
        "BPS",
        "Date of Birth",
        "First Entry in Government Service",
        "First Entry in Judiciary",
        "Current Post Date",
        "Promotion Date",
        "Retirement Date",
        "Current Posting",
        "Remarks",
    ]
    table = QTableWidget(0, len(headers))
    qtbot.addWidget(table)
    table.setHorizontalHeaderLabels(headers)

    configure_professional_table(table, settings_key="test_seniority_headers")

    assert [
        table.horizontalHeaderItem(i).text() for i in range(len(headers))
    ] == headers
    assert table.horizontalScrollMode() == QAbstractItemView.ScrollMode.ScrollPerPixel
    assert table.textElideMode() == Qt.TextElideMode.ElideRight
    assert table.columnWidth(headers.index("Full Name")) >= 220
    assert table.columnWidth(headers.index("Current Posting")) >= 180
    assert table.columnWidth(headers.index("Promotion Date")) >= 125
    assert table.columnWidth(headers.index("Remarks")) >= 220


def test_employee_summary_panel_shows_full_name_and_selectable_text(qtbot) -> None:
    panel = EmployeeSummaryPanel()
    qtbot.addWidget(panel)
    full_name = "Syed Muhammad Abdullah Shah Long Official Name"

    panel.set_summary(
        {
            "personal_number": "240303426",
            "full_name": full_name,
            "father_name": "Syed Father Name",
            "cnic_masked": "*********1234",
            "designation": "Junior Clerk",
            "bps": 11,
            "employment_status": "Active",
            "current_posting": "District Court Orakzai",
        }
    )

    full_name_label = panel.value_labels["full_name"]
    assert panel.isVisible()
    assert full_name_label.text() == full_name
    assert full_name_label.wordWrap()
    assert (
        full_name_label.textInteractionFlags()
        & Qt.TextInteractionFlag.TextSelectableByMouse
    )
