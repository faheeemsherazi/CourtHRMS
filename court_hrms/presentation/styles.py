from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


NAVY = "#0b1f3a"
NAVY_2 = "#102b4d"
GOLD = "#c9a227"
GOLD_DARK = "#a9851e"
WHITE = "#ffffff"
SURFACE = "#f5f7fb"
BORDER = "#d7dee8"
TEXT = "#1f2937"
MUTED = "#667085"
DANGER = "#b42318"
SUCCESS = "#047857"


APP_STYLE = f"""
QWidget {{
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 10pt;
    color: {TEXT};
}}

QMainWindow, QWidget#AppBackground {{
    background: {SURFACE};
}}

QFrame#LoginPanel, QFrame#Card, QGroupBox {{
    background: {WHITE};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}

QFrame#BrandPanel {{
    background: {NAVY};
    border-radius: 10px;
}}

QLabel#BrandTitle {{
    color: {WHITE};
    font-size: 24pt;
    font-weight: 700;
}}

QLabel#BrandSubtitle {{
    color: #d8e4f2;
    font-size: 11pt;
}}

QLabel#PageTitle {{
    color: {NAVY};
    font-size: 20pt;
    font-weight: 700;
}}

QLabel#SectionTitle {{
    color: {NAVY};
    font-size: 12pt;
    font-weight: 700;
}}

QLabel#Muted {{
    color: {MUTED};
}}

QLabel#MetricValue {{
    color: {NAVY};
    font-size: 24pt;
    font-weight: 700;
}}

QLabel#MetricLabel {{
    color: {MUTED};
    font-size: 10pt;
}}

QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit {{
    background: {WHITE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 9px;
    min-height: 22px;
}}

QTextEdit {{
    padding: 8px;
}}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {{
    border: 1px solid {GOLD};
}}

QPushButton {{
    background: #edf2f7;
    border: 1px solid #cfd8e3;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
}}

QPushButton:hover {{
    background: #e2e8f0;
}}

QPushButton#PrimaryButton {{
    background: {NAVY};
    border: 1px solid {NAVY};
    color: {WHITE};
}}

QPushButton#PrimaryButton:hover {{
    background: {NAVY_2};
}}

QPushButton#GoldButton {{
    background: {GOLD};
    border: 1px solid {GOLD_DARK};
    color: {NAVY};
}}

QPushButton#GoldButton:hover {{
    background: #d4b03a;
}}

QPushButton#DangerButton {{
    background: {DANGER};
    border: 1px solid {DANGER};
    color: {WHITE};
}}

QPushButton#SidebarButton {{
    background: transparent;
    border: 0;
    border-radius: 6px;
    color: #e8eef6;
    padding: 11px 14px;
    text-align: left;
    font-weight: 600;
}}

QPushButton#SidebarButton:hover {{
    background: #183b66;
}}

QPushButton#SidebarButton:checked {{
    background: {GOLD};
    color: {NAVY};
}}

QFrame#Sidebar {{
    background: {NAVY};
}}

QLabel#SidebarTitle {{
    color: {WHITE};
    font-size: 13pt;
    font-weight: 700;
}}

QLabel#SidebarSubtitle {{
    color: #cbd7e6;
    font-size: 9pt;
}}

QTableWidget {{
    background: {WHITE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    gridline-color: #e8edf3;
    selection-background-color: #d9e7f7;
    selection-color: {TEXT};
}}

QTableWidget::item {{
    padding: 7px;
}}

QHeaderView::section {{
    background: {NAVY};
    color: {WHITE};
    border: 0;
    padding: 8px;
    font-weight: 700;
}}

QGroupBox {{
    margin-top: 12px;
    padding: 14px;
    font-weight: 700;
    color: {NAVY};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    background: {WHITE};
}}

QScrollArea {{
    border: 0;
    background: transparent;
}}
"""


def apply_app_style(app: QApplication) -> None:
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(APP_STYLE)
