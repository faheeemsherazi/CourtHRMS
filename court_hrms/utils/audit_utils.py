from __future__ import annotations

import hashlib
import json
from typing import Any


SENSITIVE_KEY_PARTS = ("password", "hash", "token", "secret")


def sanitize_audit_payload(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            if any(part in str(key).lower() for part in SENSITIVE_KEY_PARTS):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = sanitize_audit_payload(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_audit_payload(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        sanitize_audit_payload(value),
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def calculate_entry_hash(payload: dict) -> str:
    canonical = canonical_json(payload)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
