# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""Diagnostics and redaction utilities for safe logging."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


# Patterns that match secrets in connection strings and similar contexts
_SECRET_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)(password\s*=\s*)([^;\s]+)"),
    re.compile(r"(?i)(pwd\s*=\s*)([^;\s]+)"),
    re.compile(r"(?i)(accountkey\s*=\s*)([^;\s]+)"),
    re.compile(r"(?i)(sharedaccesskey\s*=\s*)([^;\s]+)"),
    re.compile(r"(?i)(sig\s*=\s*)([^&\s]+)"),
    re.compile(r"(?i)(token\s*=\s*)([^;\s]+)"),
]


def redact(text: str) -> str:
    """Redact secrets from text for safe logging.
    
    Args:
        text: Input text that may contain secrets
        
    Returns:
        Text with secrets replaced by '<redacted>'
    """
    redacted = text
    for pattern in _SECRET_PATTERNS:
        redacted = pattern.sub(r"\1<redacted>", redacted)
    return redacted


@dataclass(frozen=True)
class DiagnosticPayload:
    """Container for diagnostic information with built-in redaction."""
    
    kind: str
    message: str
    details: dict[str, Any] | None = None

    def safe_message(self) -> str:
        """Get a safe-to-log message with secrets redacted.
        
        Returns:
            Redacted message suitable for logging
        """
        base = redact(self.message)
        if not self.details:
            return base
        # Avoid logging nested blobs verbatim - just show keys
        return f"{base} | details_keys={sorted(self.details.keys())}"
