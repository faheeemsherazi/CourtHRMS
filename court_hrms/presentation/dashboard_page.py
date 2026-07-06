from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from court_hrms.controllers.posting_controller import PostingController
from court_hrms.controllers.service_record_controller import ServiceRecordController
from court_hrms.controllers.staff_controller import StaffController


class DashboardPage(QWidget):
    def __init__(
        self,
        staff_controller: StaffController,
        service_record_controller: ServiceRecordController,
        posting_controller: PostingController,
    ):
        super().__init__()
        self.staff_controller = staff_controller
        self.service_record_controller = service_record_controller
        self.posting_controller = posting_controller
        self.metric_labels: dict[str, QLabel] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        title = QLabel("District Court Orakzai HR Management System")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Personnel administration dashboard")
        subtitle.setObjectName("Muted")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.addWidget(self._metric_card("Staff Profiles", "staff"), 0, 0)
        grid.addWidget(self._metric_card("Service Records", "service"), 0, 1)
        grid.addWidget(self._metric_card("Current Postings", "posting"), 0, 2)
        layout.addLayout(grid)

        summary = QFrame()
        summary.setObjectName("Card")
        summary_layout = QVBoxLayout(summary)
        summary_layout.setContentsMargins(20, 18, 20, 18)
        summary_layout.setSpacing(10)

        section_title = QLabel("System Scope")
        section_title.setObjectName("SectionTitle")
        summary_layout.addWidget(section_title)

        summary_text = QLabel(
            "This version supports secure administrator login, staff profile management, "
            "service record management, posting and transfer history, leave management, "
            "seniority lists, HR reports, printing, and secure logout for court staff."
        )
        summary_text.setWordWrap(True)
        summary_text.setObjectName("Muted")
        summary_layout.addWidget(summary_text)

        layout.addWidget(summary)
        layout.addStretch(1)

    def _metric_card(self, label: str, key: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(6)

        value = QLabel("0")
        value.setObjectName("MetricValue")
        value.setAlignment(Qt.AlignmentFlag.AlignLeft)

        caption = QLabel(label)
        caption.setObjectName("MetricLabel")

        card_layout.addWidget(value)
        card_layout.addWidget(caption)
        self.metric_labels[key] = value
        return card

    def refresh(self) -> None:
        self.metric_labels["staff"].setText(str(self.staff_controller.count_profiles()))
        self.metric_labels["service"].setText(
            str(self.service_record_controller.count_records())
        )
        self.metric_labels["posting"].setText(
            str(self.posting_controller.count_current_postings())
        )
