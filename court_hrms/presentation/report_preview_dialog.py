from __future__ import annotations

from PySide6.QtPrintSupport import QPrintPreviewDialog, QPrinter
from PySide6.QtWidgets import QWidget

from court_hrms.reporting.report_document_builder import ReportDocumentBuilder


class ReportPreviewDialog:
    @staticmethod
    def show(parent: QWidget, html: str, title: str) -> None:
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        ReportDocumentBuilder.configure_printer(printer, html)
        document = ReportDocumentBuilder.build_document(html)

        dialog = QPrintPreviewDialog(printer, parent)
        dialog.setWindowTitle(title)
        dialog.paintRequested.connect(document.print_)
        dialog.exec()
