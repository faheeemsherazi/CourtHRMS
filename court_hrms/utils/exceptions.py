from __future__ import annotations

from court_hrms.utils.validators import ValidationError


class ApplicationError(Exception):
    """Base class for non-validation application boundary errors."""


class StaffNotFoundError(ValidationError):
    """Raised when a requested staff profile cannot be found."""


class LeaveBalanceError(ValidationError):
    """Raised when a leave request exceeds the available balance."""


class LeaveDateError(ValidationError):
    """Raised when leave dates violate court HR leave rules."""


class SeniorityDataError(ValidationError):
    """Raised when seniority data cannot be generated safely."""


class ReportDataNotFoundError(ValidationError):
    """Raised when report filters do not match available HR data."""


class ReportGenerationError(ApplicationError):
    """Raised when report rendering, export, or printing fails."""


class PrinterUnavailableError(ApplicationError):
    """Raised when the operating system cannot provide a printer."""


class AuthenticationRequiredError(ValidationError):
    """Raised when a protected operation has no active authenticated admin."""


class DatabaseOperationError(ApplicationError):
    """Raised for logged database boundary failures."""
