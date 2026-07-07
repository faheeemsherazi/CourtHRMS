from __future__ import annotations


SERVICE_EVENT_TYPES = (
    "Initial Appointment",
    "Joining",
    "Confirmation",
    "Regularization",
    "Promotion",
    "Upgradation",
    "Time Scale",
    "Selection Grade",
    "Adjustment",
    "Reversion",
    "Transfer",
    "Posting",
    "Deputation",
    "Repatriation",
    "Additional Charge",
    "Suspension",
    "Reinstatement",
    "Training",
    "Leave Without Pay",
    "Resignation",
    "Retirement",
    "Compulsory Retirement",
    "Removal",
    "Dismissal",
    "Death During Service",
    "Other",
)

MOVEMENT_TYPES = (
    "First Posting",
    "Transfer",
    "Posting",
    "Adjustment",
    "Deputation",
    "Repatriation",
    "Additional Charge",
    "Temporary Duty",
    "Attachment",
    "Reposting",
    "Cancellation",
)

MOVEMENT_STATUSES = (
    "Ordered",
    "Awaiting Relieving",
    "Relieved",
    "Awaiting Joining",
    "Joined",
    "Charge Assumed",
    "Cancelled",
    "Completed",
)

TRANSFER_CATEGORIES = (
    "Administrative",
    "Own Request",
    "Public Interest",
    "Promotion",
    "Adjustment",
    "Mutual",
    "Temporary",
    "Other",
)

DOCUMENT_TYPES = (
    "Appointment Order",
    "Posting Order",
    "Transfer Order",
    "Promotion Order",
    "Upgradation Order",
    "Leave Sanction Order",
    "Medical Certificate",
    "Joining Report",
    "Relieving Report",
    "Charge Assumption Report",
    "Retirement Order",
    "Pension Document",
    "Seniority Objection",
    "Seniority Decision",
    "Show-Cause Notice",
    "Inquiry Order",
    "Penalty Order",
    "Appeal Order",
    "Other",
)

SENIORITY_LIST_TYPES = (
    "Working",
    "Draft",
    "Tentative",
    "Final",
    "Revised Final",
)

SENIORITY_LIST_STATUSES = (
    "Generated",
    "Under Verification",
    "Circulated",
    "Objections Open",
    "Objections Closed",
    "Finalized",
    "Superseded",
)

SENIORITY_OBJECTION_STATUSES = (
    "Received",
    "Under Review",
    "Accepted",
    "Partially Accepted",
    "Rejected",
    "Disposed",
)
