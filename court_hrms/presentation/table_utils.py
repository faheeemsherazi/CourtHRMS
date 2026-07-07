from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHeaderView,
    QLabel,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
)


@dataclass(frozen=True)
class ColumnRule:
    minimum: int = 100
    resize_mode: QHeaderView.ResizeMode = QHeaderView.ResizeMode.Interactive
    stretch: bool = False


_WIDTH_CACHE: dict[str, dict[int, int]] = {}


def make_table_item(
    value,
    *,
    user_data=None,
    alignment: Qt.AlignmentFlag | Qt.Alignment = Qt.AlignmentFlag.AlignLeft,
) -> QTableWidgetItem:
    text = "" if value is None else str(value)
    item = QTableWidgetItem(text)
    item.setData(Qt.ItemDataRole.ToolTipRole, text)
    if user_data is not None:
        item.setData(Qt.ItemDataRole.UserRole, user_data)
    item.setTextAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
    return item


def configure_professional_table(
    table: QTableWidget,
    column_rules: Mapping[int | str, ColumnRule | dict] | None = None,
    *,
    enable_row_details: bool = True,
    settings_key: str | None = None,
) -> None:
    _ = enable_row_details
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    table.setTextElideMode(Qt.TextElideMode.ElideRight)
    table.setAlternatingRowColors(True)

    header = table.horizontalHeader()
    header.setMinimumSectionSize(90)
    header.setStretchLastSection(False)
    header.setSectionsMovable(False)
    header.setSectionsClickable(True)

    resolved_rules = _resolve_column_rules(table, column_rules or {})
    for column in range(table.columnCount()):
        header_item = table.horizontalHeaderItem(column)
        header_text = header_item.text() if header_item is not None else ""
        if header_item is not None:
            header_item.setData(Qt.ItemDataRole.ToolTipRole, header_text)

        rule = resolved_rules[column]
        header.setSectionResizeMode(column, rule.resize_mode)
        if rule.resize_mode == QHeaderView.ResizeMode.Interactive:
            header.resizeSection(column, rule.minimum)
        table.setColumnWidth(column, max(table.columnWidth(column), rule.minimum))

    if settings_key:
        for column, width in _WIDTH_CACHE.get(settings_key, {}).items():
            if 0 <= column < table.columnCount():
                table.setColumnWidth(column, width)

        def _remember_width(index: int, _old_size: int, new_size: int) -> None:
            _WIDTH_CACHE.setdefault(settings_key, {})[index] = new_size

        header.sectionResized.connect(_remember_width)


def apply_full_text_tooltips(table: QTableWidget) -> None:
    for row in range(table.rowCount()):
        for column in range(table.columnCount()):
            item = table.item(row, column)
            if item is not None:
                item.setData(Qt.ItemDataRole.ToolTipRole, item.text())


def _resolve_column_rules(
    table: QTableWidget,
    explicit_rules: Mapping[int | str, ColumnRule | dict],
) -> dict[int, ColumnRule]:
    rules: dict[int, ColumnRule] = {}
    for column in range(table.columnCount()):
        header_item = table.horizontalHeaderItem(column)
        header = header_item.text() if header_item is not None else ""
        rule = _rule_for_header(header)
        if column in explicit_rules:
            rule = _coerce_rule(explicit_rules[column])
        elif header in explicit_rules:
            rule = _coerce_rule(explicit_rules[header])
        rules[column] = rule
    return rules


def _coerce_rule(value: ColumnRule | dict) -> ColumnRule:
    if isinstance(value, ColumnRule):
        return value
    return ColumnRule(**value)


def _rule_for_header(header: str) -> ColumnRule:
    normalized = header.lower()
    if "id" == normalized or normalized.endswith(" id"):
        return ColumnRule(70, QHeaderView.ResizeMode.ResizeToContents)
    if "personal" in normalized:
        return ColumnRule(135, QHeaderView.ResizeMode.ResizeToContents)
    if "father" in normalized:
        return ColumnRule(180)
    if "name" in normalized:
        return ColumnRule(220)
    if "designation" in normalized:
        return ColumnRule(150)
    if normalized in {"bps", "rank", "days", "year"} or "merit" in normalized:
        return ColumnRule(95, QHeaderView.ResizeMode.ResizeToContents)
    if (
        "date" in normalized
        or "appointment" in normalized
        or "promotion" in normalized
        or "entry" in normalized
    ):
        return ColumnRule(125)
    if "station" in normalized or "posting" in normalized:
        return ColumnRule(180)
    if "status" in normalized or normalized == "current":
        return ColumnRule(120, QHeaderView.ResizeMode.ResizeToContents)
    if "remarks" in normalized or "reason" in normalized:
        return ColumnRule(220)
    return ColumnRule(115)


class EmployeeSummaryPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.value_labels: dict[str, QLabel] = {}

        layout = QGridLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(6)

        fields = [
            ("Personal Number", "personal_number"),
            ("Full Name", "full_name"),
            ("Father's Name", "father_name"),
            ("CNIC", "cnic_masked"),
            ("Designation", "designation"),
            ("BPS", "bps"),
            ("Employment Status", "employment_status"),
            ("Current Posting", "current_posting"),
        ]
        for index, (label_text, key) in enumerate(fields):
            row = index // 2
            col = (index % 2) * 2
            label = QLabel(label_text)
            label.setObjectName("Muted")
            value = QLabel("")
            value.setWordWrap(True)
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            value.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Preferred,
            )
            layout.addWidget(label, row, col)
            layout.addWidget(value, row, col + 1)
            self.value_labels[key] = value

        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        self.setVisible(False)

    def set_summary(self, data: dict | None) -> None:
        if not data:
            self.clear()
            return
        for key, label in self.value_labels.items():
            value = data.get(key)
            label.setText("" if value is None else str(value))
        self.setVisible(True)

    def clear(self) -> None:
        for label in self.value_labels.values():
            label.clear()
        self.setVisible(False)
