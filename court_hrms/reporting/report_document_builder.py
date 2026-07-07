from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QMarginsF
from PySide6.QtGui import QPageLayout, QPageSize, QTextDocument
from PySide6.QtPrintSupport import QPrinter

from court_hrms.utils.exceptions import ReportGenerationError
from court_hrms.utils.report_utils import ensure_pdf_suffix


class ReportDocumentBuilder:
    @staticmethod
    def build_document(html: str) -> QTextDocument:
        document = QTextDocument()
        document.setHtml(html)
        return document

    @staticmethod
    def configure_printer(printer: QPrinter, html: str | None = None) -> None:
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setPageOrientation(ReportDocumentBuilder.page_orientation(html))
        printer.setPageMargins(
            QMarginsF(12, 12, 12, 12),
            QPageLayout.Unit.Millimeter,
        )

    @staticmethod
    def page_orientation(html: str | None) -> QPageLayout.Orientation:
        if html and 'name="report-orientation" content="landscape"' in html:
            return QPageLayout.Orientation.Landscape
        return QPageLayout.Orientation.Portrait

    def export_pdf(self, html: str, output_path: str | Path) -> Path:
        output_path = ensure_pdf_suffix(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(str(output_path))
        self.configure_printer(printer, html)

        document = self.build_document(html)
        try:
            document.print_(printer)
        except Exception as exc:
            raise ReportGenerationError(
                "The PDF report could not be generated."
            ) from exc

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise ReportGenerationError("The PDF report could not be generated.")
        return output_path
